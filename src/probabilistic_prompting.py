import pandas as pd
import openai
import time
from typing import List
import os
from pathlib import Path

# in parallel make calls and write to jsonl file

import fire

import json
import threading
import fcntl
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

import random


from utils import write_result, filter_seen_solutions, call_oai_rm_llm, question_to_category
# get t from command line
       

def get_specialized_prompt(entry):
    specialized_prompt = entry['prompt'] + "\n\n Additional instructions: \n" 
    for i, option in enumerate(entry['options'].values()): 
        choices = list(option.items())
        
        
        odds = choices[0][1]
        # sample boolean True with odds 
        first_taken = random.choices([True, False], weights=[odds, 1-odds])[0]
        if first_taken:
            specialized_prompt += f"{i+1}. {choices[0][0]}\n"
        else:
            specialized_prompt += f"{i+1}. {choices[1][0]}\n"
    category = question_to_category(entry['prompt'], natural = True)
    return specialized_prompt + f"\n If no {category} fits the instructions, respond INVALID." 

def process_prompt(entry, existing_entry, i, T, max_tokens, n=100):
    if existing_entry == None:
        final_specialized_prompts = []
        final_outputs = []
        invalids_seen = 0
        retry= False
    else: 
        final_specialized_prompts = existing_entry['specialized_prompt']
        final_outputs = existing_entry['completions']
        invalids_seen = existing_entry['invalids_seen']
        retry = True
    
    for i in range(15):
        specialized_prompts = [get_specialized_prompt(entry) for _ in range(n - len(final_outputs))]
        
        # tabulate how many of each unique prompt there is
        prompt_counts = {}
        for prompt in specialized_prompts:
            if prompt in prompt_counts:
                prompt_counts[prompt] += 1
            else:
                prompt_counts[prompt] = 1
                
        outputs = {prompt:  call_oai_rm_llm(prompt, n=count, temperature=T, model_id="gpt-4o", max_tokens=max_tokens) for prompt,count in prompt_counts.items() }
        outputs = {k: [v] if isinstance(v, str) else v for k, v in outputs.items() }
        for p, os in outputs.items(): 
            for o in os:
                if o == "INVALID":
                    invalids_seen += 1
                    continue
                if o == None: 
                    continue
                else: 
                    final_specialized_prompts.append(p)
                    final_outputs.append(o) 
        if i == 0 and len (final_outputs) <= n*0.1:
            break
        if i > 2 and len (final_outputs) <= n*0.5:
            break
        if i > 5 and len(final_outputs) <= n*0.75:
            break 
        if i > 8 and len(final_outputs) <= n*0.9:
            break
        if retry == True: 
            break
    
    if len(final_outputs) != n:
        print (f"Not enough outputs for {entry['idx']}: {len(final_outputs)}")
    
        
    result = {
        "idx": entry['idx'],
        "prompt": entry['prompt'],
        "specialized_prompt": final_specialized_prompts,
        "completions": final_outputs, 
        "invalids_seen": invalids_seen,
    }
    return result


def process_and_write(prompt, in_prog, output_file, i, T, max_tokens):
    result = process_prompt(prompt, in_prog, i, T, max_tokens)
    if result:
        write_result(result, output_file)
    print(f"Processed {i} prompts")

def probabilistic_prompting(T, R, infile, max_tokens = 50):

    output_file = f'final_data/ss_completions_temp_{str(T)}-rep-{R}.jsonl'

    if os.path.exists(output_file):
        raise Exception("Output file already exists")

    with open(infile, 'r') as f:
        entries = [json.loads(line) for line in f.readlines()]

    # entries = filter_seen_solutions(entries, output_file)
    if len(entries) == 0:
        print(f"No new prompts to process for temperature {T}")
        exit()

    entries_to_process = [
        (i, e, None)
        for i, e in enumerate(entries)
    ]

    # Process prompts in parallel
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(process_and_write, entry, in_prog_e, output_file, i, T, max_tokens)
            for i, entry, in_prog_e in entries_to_process
        ]
        
        # Wait for all futures to complete
        for future in futures:
            future.result()


if __name__ == "__main__":
    fire.Fire(probabilistic_prompting)

    
    
