import os
import json
import fcntl
import time
import openai
from typing import List
import anthropic



def write_result(result, output_file):
    if result is None:
        return
        
    with open(output_file, 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(result) + '\n')
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def get_coverage_qa_prompts(prompt_file): 
    prompts = json.load(open(prompt_file, 'r'))
    return list(prompts.keys())

def filter_seen_solutions(solutions, output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            seen_prompts = [json.loads(line)['prompt'] for line in f.readlines()]
        return [sol for sol in solutions if sol['prompt'] not in seen_prompts]
    return solutions

def question_to_category(question, natural = False):
    if "country" in question:
        category = "country" 
    elif "music" in question: 
        category = "musical instrument" if natural else "instrument"
    elif "chemical" in question:
        category = "periodic table element" if natural else "chemical"
    elif "Associated Press Athlete of the Year" in question: 
        category = "athlete"
    elif "physic" in question.lower():
        category = "physicist" if natural else "physic"
    elif "park" in question.lower():
        category = "national park" if natural else "park"
    else: 
        raise NotImplementedError

    return category

def call_anth_rm_llm(
    prompt: str,
    n: int = 1,
    temperature: float = 1.0,
    model_id: str = "claude-3-7-sonnet-20250219",
    system_prompt = None,
    retry_count: int = 1e9,
    max_tokens: int = 1000,
) -> List[str]:
    client = anthropic.Client()
    

    backoff = 1
    retry_count = int(retry_count)
    if system_prompt:
        messages = [ {"role": "user", "content": prompt}]
    else:
        messages = [ {"role": "user", "content": prompt}]
        
    all_responses = []
    for i in range(n):
        for attempt in range(retry_count):
            try: 
                if system_prompt:
                    response = client.messages.create(
                        model=model_id,  
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=messages,
                        system = system_prompt,
                    )
                else:
                    response = client.messages.create(
                        model=model_id,  
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=messages,
                    )
                # print (response)
                response = response.content[0].text
                break
            except Exception as e:
                if "429" in str(e):
                    print("Retry due to rate limit: ", e)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 64)  # Exponential backoff up to 64s
                    continue
                else:
                    print("Exception: ", e)
                    return []
        else: 
            print (f"Failed to get a valid result for prompt {prompt} after {retry_count} attempts")
            
        all_responses.append(response)
        if temperature == 0: 
            all_responses = [response]*n
            break

    if n == 1:
        return all_responses[0]
    return all_responses

def call_oai_rm_llm(
    prompt: str,
    n: int = 1,
    temperature: float = 1.0,
    model_id: str = "gpt-4o",
    system_prompt = None,
    retry_count: int = 1e9,
    max_tokens: int = 1000,
) -> List[str]:
    client = openai.OpenAI()

    backoff = 1
    retry_count = int(retry_count)
    if system_prompt:
        messages = [ {"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    else:
        messages = [ {"role": "user", "content": prompt}]
    for attempt in range(retry_count):
        try: 
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                n=n,
                max_tokens=max_tokens,
            )
            break
        except Exception as e:
            if "429" in str(e):
                print("Retry due to rate limit: ", e)
                time.sleep(backoff)
                backoff = min(backoff * 2, 64)  # Exponential backoff up to 64s
                continue
            else:
                print("Exception: ", e)
                return []

    if n == 1:
        return response.choices[0].message.content
    return [choice.message.content for choice in response.choices]
def write_result(result, output_file):
    if result is None:
        return
        
    with open(output_file, 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(result) + '\n')
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            
SYSTEM_SUPERFORECASTER_0 = """You are an expert superforecaster, familiar with the work of Tetlock and others.
Your mission is to generate accurate predictions for forecasting questions.
Aggregate the information provided by the user. Make sure to give detailed reasonings."""