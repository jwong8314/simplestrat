import pandas as pd
import openai
import time
from typing import List
import re
import os
import fire

from prompts import heuristic_estimation_prompt_format
from utils import get_coverage_qa_prompts
from parsers import heuristic_estimation_parse_result
from utils import write_result

import json
import threading
import fcntl
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from utils import filter_seen_solutions, question_to_category

from utils import call_oai_rm_llm, SYSTEM_SUPERFORECASTER_0, call_anth_rm_llm


def heuristic_estimation(infile, anth = False, max_length = 1000):
    
    anth_tag = '_anth' if anth else ''
    # Read prompts from CSV
    with open (infile, 'r') as f:
        entries = f.readlines()
        entries = [json.loads(entry) for entry in entries]
        

    output_file = f'odds{anth_tag}.jsonl'

    if os.path.exists(output_file):
        entries = filter_seen_solutions(entries, output_file)
    else:
        # Create/clear the output file
        open(output_file, 'w').close()

    print (f"Processing {len(entries)} prompts out of {len(entries)} total prompts")

    # Process prompts in parallel
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(process_and_write, entry, output_file, i, n_prompts = len(entries), anth=anth)
            for i, entry in enumerate(entries)
        ]
        
        # Wait for all futures to complete
        for future in futures:
            future.result()
        
# in parallel make calls and write to jsonl file

def process_option(option, prompt, max_attempts=5, anth=False):
    option_title = option['name']
    option_results = {}
    opt_choices = option['options']
    # turn the first character to lowercase
    def get_opt(opt_choice):
        opt = opt_choice[0].lower() + opt_choice[1:]
        opt = opt.strip()
        if opt[-1] == '.':
            opt = opt[:-1]
        return opt
    
    optA = get_opt(opt_choices[0])
    optB = get_opt(opt_choices[1])
    category = question_to_category(prompt)
    prompt_formatted = heuristic_estimation_prompt_format.format(request=prompt, axisA = optA, axisB = optB, category = category )
    for i in range(max_attempts):
        fn = call_anth_rm_llm if anth else call_oai_rm_llm 
        model = "claude-3-7-sonnet-20250219" if anth else "gpt-4o"
        outputs = fn(prompt_formatted, n=1, temperature=0.2, model_id=model, system_prompt=SYSTEM_SUPERFORECASTER_0)
        if not outputs:
            return None
        
        parsed_result = heuristic_estimation_parse_result(outputs)
        
        # if string is float
        if parsed_result.replace('.', '', 1).isdigit():
            odds = float(parsed_result)
            option_results[optA] = 1 - odds
            option_results[optB] = odds
            break
        else:
            print (f"Failed to parse result for {option_title} {parsed_result}")
            continue
    else: 
        return None
    return option_results


def process_prompt(entry, max_attempts=5, anth = False):
    idx = entry['idx']
    prompt = '"' + entry['prompt'] + '"'
    all_results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for option in entry['options']:
            future = executor.submit(process_option, option, prompt, anth = anth)
            futures.append((option['name'], future))
        
        for option_title, future in futures:
            option_results = future.result()
            if option_results is not None:
                all_results[option_title] = option_results
                    
    result = {
        "idx": idx,
        "prompt": entry['prompt'],
        "options": all_results, # has odds
        
    }
        
    return result

def process_and_write(prompt, output_file, i, n_prompts, anth = False):
    result = process_prompt(prompt, anth = anth)
    if result:
        write_result(result, output_file)
    print(f"Processed {i} of {n_prompts} prompts")



if __name__ == "__main__":
    # Example usage: python heuristic_estimation.py --infile=modified_prompts.jsonl
    fire.Fire(heuristic_estimation)
    
    
