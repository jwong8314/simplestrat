import json
import pandas as pd
from utils import question_to_category
from typing import List   
def is_equal (A,B, category = None):
    if category == 'athlete':
        return A.split(" ")[-1].lower() == B.split(" ")[-1].lower()
    else:
        return A.lower() == B.lower()
    
def check_recall(ans: List[str], answer_equiv_gt: List[str], category = None): 
    for answer in ans: 
        if  any (is_equal(a,answer) for a in answer_equiv_gt): 
            return True
    else: 
        return False
    
    
def get_recall(ans: List[str], GT: List[List[str]], category: str = None): 
    stats = [check_recall(ans, answer_group_gt, category = category) for answer_group_gt in GT]
    recall = (sum(stats)/ len(stats))
    return recall

def idx_to_prompt(idx):
    pd.read_csv('prompts_final.csv')
    # turn this into a dictionary idx: prompt
    prompts_df = pd.read_csv('prompts_final.csv')
    # there's a column called 'idx' and a column called 'prompt'
    prompts = prompts_df['prompt'].tolist()
    idxs = prompts_df['idx'].tolist()
    prompts = {idx: prompt for idx, prompt in zip(idxs, prompts)}
    return prompts[idx]

def get_answers_from_file(file):
    with open(file, 'r') as f:
        entries = f.readlines()
        entries = [json.loads(entry) for entry in entries]
    return entries
