auto_strat_prompt_format = """I am tasked with the following request: 
{user_request}

Help me brainstorm how to respond to the user request by providing a list of True/False properties the solution may or may not have. Use the following step-by-step to come up with good properties: 

1. If you were playing 20 questions, what's a good first question to ask that would split the possibilites in half? 
List at least 4 questions and their corresponding properties.
Question: <Description>

2. Rewrite each question as a True/False property that's true for one half and false for the other.
Question: <Description>
True/False Property: <Property Description>

3. For each property, come up with an example that would satisfy the property.
Property: <Description>
Example: <Description>
Is it a valid answer to the user's request? <Yes/No>

4. For each property, come up with an example that would not satisfy the property.
Property: <Description>
Example: <Description>
Is it a valid answer to the user's request? <Yes/No>

5. For each property, list whether we should include it or not in the final list of properties. Do not include ones where an example from above is not valid.
Property: <Description>
Include in final list? <Yes/No>

List the properties in the following format where + indicates the property and - indicates it's negation.
Avoid abbreviation in final answer. Minimum 4 properties.

FINAL ANSWER: 

1. **<Name of Property>**
+ The {category} ... <Option 1>
- The {category} ... <Option 2>

Ensure all properties are listed are sentences that are either True or False.
"""

heuristic_estimation_prompt_format = """I am tasked to estimate the probability that a random {category} picked by participants based on the prompt {request} is A) {axisA} or B) {axisB}. 
                  
Instructions:
1. Provide a reason or example why the answer might be A based on the prompt.
{{ Insert your thoughts }}

2. Provide a reason or example why the answer might be B based on the prompt.
{{ Insert your thoughts }}

3. Rate the strength of each of the reasons given in the last two responses. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your rating of the strength of each reason }}

4. Aggregate your considerations.
{{ Insert your aggregated considerations }}

5. Rate which one is more likely. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal. 
0 is A, 0.3 is A is more likely than B, 0.5 is equal, 0.7 is B is more likely than A, 1 is B. 
{{ Insert your answer }}
"""