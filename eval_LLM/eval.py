import json
import re
import os

empty_prediction_count = 0  
unmatched_prediction_count = 0  

import re

def extract_method_before_backslash(text):
    global empty_prediction_count, unmatched_prediction_count

    if not text.strip():
        empty_prediction_count += 1
        unmatched_prediction_count += 1
        return ''

    match = re.search(r"\b[A-Za-z0-9_][A-Za-z0-9_]{1,}\b", text)
    if match:
        return match.group(0)

    unmatched_prediction_count += 1
    return ''


input_path = 'eval_LLM/CodeLlama-13b-Instruct-hf/rq3/CodeLlama-13b_rq3.jsonl'
base_dir = os.path.dirname(input_path)

gold_path = os.path.join(base_dir, 'CodeLlama-13b_rq3.gold')
output_path = os.path.join(base_dir, 'CodeLlama-13b_rq3.output')

line_count = 0

with open(input_path, 'r', encoding='utf-8') as fin, \
     open(gold_path, 'w', encoding='utf-8') as f_gold, \
     open(output_path, 'w', encoding='utf-8') as f_output:

    for line in fin:
        data = json.loads(line)
        method_name = data.get('method_name', '')
        prediction = data.get('prediction', '')

        f_gold.write(method_name + '\n')

        extracted = extract_method_before_backslash(prediction)
        f_output.write(extracted + '\n')

        line_count += 1

print(f'Total lines processed: {line_count}')
print(f'Empty prediction lines: {empty_prediction_count}')
print(f'Unmatched prediction lines: {unmatched_prediction_count}')
