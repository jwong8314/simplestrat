import re
def auto_strat_parse_result(result):
    # result is in the format of 1. <Name of Choice> - The story ... <Option 1> - The story ... <Option 2>
    # 2. <Name of Choice> - The story ... <Option 1> - The story ... <Option 2>
    # ...
    # 5. <Name of Choice> - The story ... <Option 1> - The story ... <Option 2>
    
    options = [] # name of choice, option 1, option 2
    
    # ignore everything until "FINAL ANSWER:"
    result = result.split("FINAL ANSWER:")
    if len(result) < 2:
        return []
    result = result[1]
    
    # split by line
    lines = result.split('\n')
    current_option = {}
    for line in lines:
        if len(line) < 2:
            continue
        if line[0].isdigit() and line[1] == '.':
            # we're in a new option
            if current_option:
                options.append(current_option)
            current_option = {}
            current_option['name'] = line[2:].strip().replace('**', '')
            current_option['options'] = []
            
        if line.strip().startswith('-'):
            current_option['options'].append(line.strip().replace('-', '').strip())
        elif line.strip().startswith('+'):
            current_option['options'].append(line.strip().replace('+', '').strip())
    else: 
        if current_option:
            options.append(current_option)
    return options

def heuristic_estimation_parse_result(result):
    # things between ** and ** regex number
    options = re.findall(r'\*([0-9]*\.?[0-9]+)\*', result)
    return options[0]