import json

def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line.strip())

def read_text_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def apply_dictionary_replacement(text, name_map):

    result = text
    sorted_mappings = sorted(name_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for original_key, mapped_value in sorted_mappings:
        import re
        pattern = re.compile(re.escape(original_key), re.IGNORECASE)
        
        matches = list(pattern.finditer(result))
        
        for match in reversed(matches):
            start, end = match.span()
            result = result[:start] + mapped_value + result[end:]
    
    return result

def main():
    dict_file = 'processed_code2vec_data/v3/train.jsonl'
    gold_file = 'saved_models_round7/target_length_16/test_no_verb_ppl/test_0.gold'
    result_file = 'saved_models_round7/test_0.gold_transformed'
    
    print("Starting to process files...")
    
    # Read all files
    print("Reading dictionary file...")
    dict_records = list(read_jsonl(dict_file))
    
    print("Reading gold file...")
    gold_lines = read_text_lines(gold_file)
    
    if len(dict_records) != len(gold_lines):
        print(f"Warning: File line counts are inconsistent!")
        print(f"Dictionary file: {len(dict_records)} lines")
        print(f"Gold file: {len(gold_lines)} lines") 
        min_lines = min(len(dict_records), len(gold_lines))
        print(f"Will process the first {min_lines} lines")
    else:
        min_lines = len(dict_records)
        print(f"File line counts are consistent, total {min_lines} lines")
    
    transformed_lines = []
    replacement_count = 0
    total_replacements = 0
    
    for i in range(min_lines):
        dict_record = dict_records[i]
        gold_line = gold_lines[i]
        
        name_map = dict_record.get('name_map', {})
        
        if not name_map:
            transformed_lines.append(gold_line)
            continue
        
        transformed_line = apply_dictionary_replacement(gold_line, name_map)
        transformed_lines.append(transformed_line)

        if transformed_line != gold_line:
            replacement_count += 1
            import re
            line_replacements = 0
            for key in name_map.keys():
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                matches = pattern.findall(gold_line)
                line_replacements += len(matches)
            total_replacements += line_replacements
            
            print(f"Line {i+1}: '{gold_line}' -> '{transformed_line}' (replaced {line_replacements} identifiers)")
    
    print(f"\nSaving transformed file to: {result_file}")
    with open(result_file, 'w', encoding='utf-8') as f:
        for line in transformed_lines:
            f.write(line + '\n')
    
    print(f"\nProcessing complete!")
    print(f"Total processed lines: {min_lines}")
    print(f"Lines with changes: {replacement_count}")
    print(f"Total replacements: {total_replacements}")
    
    print(f"\nStatistics:")
    total_mappings = sum(len(record.get('name_map', {})) for record in dict_records[:min_lines])
    print(f"Total mappings in dictionary: {total_mappings}")
    print(f"Line change rate: {replacement_count/min_lines*100:.2f}%")
    if total_mappings > 0:
        print(f"Mapping usage rate: {total_replacements/total_mappings*100:.2f}%")



if __name__ == '__main__':
    main()