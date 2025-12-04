import pandas as pd
import openai
import time
from typing import List
from prompts import auto_strat_prompt_format
from parsers import auto_strat_parse_result 
from utils import write_result

import fire

import os
import json
import threading
import fcntl
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from utils import question_to_category

from utils import call_oai_rm_llm, call_anth_rm_llm

from utils import get_coverage_qa_prompts

def auto_stratification(prompt_file, max_length = 5000, anth = False):

    # Get prompts
    prompts = get_coverage_qa_prompts(prompt_file)

    anth_tag = '_anth' if anth else ''
    output_file = f'modified_prompts{anth_tag}.jsonl'
    
    if not os.path.exists(output_file):
        # Create/clear the output file
        open(output_file, 'w').close()

    prompts_to_process = list(enumerate(prompts))

    with open(output_file, 'r') as f:
        entries = [json.loads(line) for line in f.readlines()]
        seen_idx = set(entry['idx'] for entry in entries)

    prompts_to_process = [
        (i, prompt) for i, prompt in prompts_to_process
        if i not in seen_idx
    ]

    print (f"Processing {len(prompts_to_process)} prompts out of {len(prompts)} total prompts")
    # Process prompts in parallel
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(process_and_write, prompt, output_file, i, n_prompts=len(prompts), anth=anth, max_length=max_length)
            for i, prompt in prompts_to_process
        ]
        
        # Wait for all futures to complete
        for future in futures:
            future.result()

def process_prompt(prompt, idx, max_attempts=5, anth=False, max_length=5000 ):
    category = question_to_category(prompt, natural = True) # hacky should use db
    prompt_formatted = auto_strat_prompt_format.format(user_request=prompt, category=category)
    for i in range(max_attempts):
        fn = call_anth_rm_llm if anth else call_oai_rm_llm 
        model = "claude-3-7-sonnet-20250219" if anth else "gpt-4o"
        outputs = fn(prompt_formatted, n=1, temperature=0.5, model_id=model, max_tokens=max_length)
        if not outputs:
            return None
        
        parsed_result = auto_strat_parse_result(outputs)
        if len(parsed_result) <= 3:
            continue
        else:
            result = {
                "idx": idx, 
                "prompt": prompt,
                "raw_result": outputs,
                "options": auto_strat_parse_result(outputs)
            }
            break
    else: 
        print (f"Failed to get a valid result for prompt {prompt} after {max_attempts} attempts")
        return None
    return result

def process_and_write(prompt, output_file, i, n_prompts = None, anth=False, max_length=5000):
    result = process_prompt(prompt, i, anth, max_length)
    if result:
        write_result(result, output_file)
    print(f"Processed {i} of {n_prompts} prompts")

if __name__ == "__main__":
    # Example usage: python autostratification.py --prompt_file=data/CoverageQA.json 
    fire.Fire(auto_stratification)



    
    
