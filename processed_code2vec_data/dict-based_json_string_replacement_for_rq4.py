import json
import argparse
import re

def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line.strip())

import json
import random
import string
import os
import re
from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language('eval_LLM/build', 'java')

class JavaASTExtractor:
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

    def parse_code(self, code):
        return self.parser.parse(bytes(code, "utf8"))

    def construct_dict(self, node, dict):
        if node.type == "return_statement" or node.type== "yield_statement" or node.type== "yield_statement" or node.type == "enhanced_for_statement":
            for child in node.children:
                if child.type == "identifier":
                    name = child.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        if node.type == "formal_parameters" or node.type == "variable_declarator":
            for descendant in self.get_all_descendants(node):
                if descendant.type == "identifier":
                    name = descendant.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        if node.type == "assignment_expression":
            left = node.child_by_field_name('left')
            for descendant in ([left] if left.type == "identifier" else self.get_all_descendants(left)):
                if descendant.type == "identifier":
                    name = descendant.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        for child in node.children:
            self.construct_dict(child, dict)

    def get_all_descendants(self, node, lst=None):
        if lst is None:
            lst = []
        for c in node.children:
            lst.append(c)
            self.get_all_descendants(c, lst)
        return lst

def replace_identifiers(root, code, name_map):
    edits = []
    def visit(n):
        if n.type == "identifier":
            nm = n.text.decode("utf-8")
            if nm in name_map:
                edits.append((n.start_byte, n.end_byte, name_map[nm]))
        for c in n.children:
            visit(c)
    visit(root)
    for s, e, txt in sorted(edits, key=lambda x: -x[0]):
        code = code[:s] + txt + code[e:]
    return code

def replace_method_names(root, code, name_map):

    edits = []
    
    def visit(n):
        if n.type == "method_declaration":
            methodname_node = n.child_by_field_name('name')
            if methodname_node:
                original_method_name = methodname_node.text.decode("utf-8")
                new_method_name = apply_dictionary_replacement(original_method_name, name_map)
                if new_method_name != original_method_name:
                    edits.append((methodname_node.start_byte, methodname_node.end_byte, new_method_name))
        
        for c in n.children:
            visit(c)
    
    visit(root)
    
    for s, e, txt in sorted(edits, key=lambda x: -x[0]):
        code = code[:s] + txt + code[e:]
    
    return code

def apply_dictionary_replacement(text, name_map):

    result = text
    sorted_mappings = sorted(name_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for original_key, mapped_value in sorted_mappings:
        pattern = re.compile(re.escape(original_key), re.IGNORECASE)
        
        matches = list(pattern.finditer(result))
        
        for match in reversed(matches):
            start, end = match.span()
            result = result[:start] + mapped_value + result[end:]
    
    return result

def random_string(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def find_all_java_files(directory):
    java_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files

def process_java_files(input_directory, output_directory=None):
    extractor = JavaASTExtractor()
    
    java_files = find_all_java_files(input_directory)
    print(f"Found {len(java_files)} java files")
    
    for i, file_path in enumerate(java_files):
        print(f"Processing {i+1}/{len(java_files)}: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = extractor.parse_code(code)
            root = tree.root_node
            
            name_map = {}
            extractor.construct_dict(root, name_map)
            
            modified_code = replace_identifiers(root, code, name_map)
            
            tree_modified = extractor.parse_code(modified_code)
            root_modified = tree_modified.root_node
            
            final_code = replace_method_names(root_modified, modified_code, name_map)
            
            if output_directory:
                relative_path = os.path.relpath(file_path, input_directory)
                output_path = os.path.join(output_directory, relative_path)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                output_path = file_path
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            print(f"  - Replaced {len(name_map)} identifiers")
            if name_map:
                print(f"  - Dictionary example: {dict(list(name_map.items())[:3])}")
        
        except Exception as e:
            print(f"  - Error processing file: {str(e)}")
            continue


def main():
    parser = argparse.ArgumentParser(description='Apply dictionary-based string replacement to method names')
    parser.add_argument('--dict_file', required=True, help='Path to the dictionary JSONL file containing name_map')
    parser.add_argument('--inp_file', required=True, help='Path to the input JSONL file (similar to built_data_for_rq4.py format)')
    parser.add_argument('--out_file', required=True, help='Path to the output JSONL file')
    
    args = parser.parse_args()
    
    dict_file = args.dict_file
    inp_file = args.inp_file
    out_file = args.out_file

    dict_records = list(read_jsonl(dict_file))
    
    inp_records = list(read_jsonl(inp_file))
    
    if len(dict_records) != len(inp_records):
        print(f"Warning: File line counts are inconsistent!")
        print(f"Dictionary file: {len(dict_records)} lines")
        print(f"Input file: {len(inp_records)} lines") 
        min_lines = min(len(dict_records), len(inp_records))
        print(f"Will process the first {min_lines} lines")
    else:
        min_lines = len(dict_records)
        print(f"File line counts are consistent, total {min_lines} lines")
    
    # Process each line
    transformed_records = []
    replacement_count = 0
    total_replacements = 0
    
    for i in range(min_lines):
        dict_record = dict_records[i]
        inp_record = inp_records[i].copy()  # Copy original record
        
        # Get the name_map dictionary for current line
        name_map = dict_record.get('name_map', {})
        
        # Get original method_name
        original_method_name = inp_record.get('method_name', '')
        
        if not name_map or not original_method_name:
            # If no name_map or method_name, keep as is
            transformed_records.append(inp_record)
            continue
        
        # Apply dictionary replacement to method_name
        transformed_method_name = apply_dictionary_replacement(original_method_name, name_map)
        inp_record['method_name'] = transformed_method_name
        transformed_records.append(inp_record)
        
        # Count replacement statistics
        if transformed_method_name != original_method_name:
            replacement_count += 1
            # Count how many replacements were made in this line (case insensitive)
            line_replacements = 0
            for key in name_map.keys():
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                matches = pattern.findall(original_method_name)
                line_replacements += len(matches)
            total_replacements += line_replacements
            
            print(f"Line {i+1}: '{original_method_name}' -> '{transformed_method_name}' (replaced {line_replacements} identifiers)")
    
    # Save results
    print(f"\nSaving transformed file to: {out_file}")
    with open(out_file, 'w', encoding='utf-8') as f:
        for record in transformed_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"\nProcessing completed!")
    print(f"Total processed lines: {min_lines}")
    print(f"Lines with changes: {replacement_count}")
    print(f"Total replacements: {total_replacements}")
    
    # Display some statistics
    print(f"\nStatistics:")
    total_mappings = sum(len(record.get('name_map', {})) for record in dict_records[:min_lines])
    print(f"Total mappings in dictionary: {total_mappings}")
    print(f"Line change rate: {replacement_count/min_lines*100:.2f}%")
    if total_mappings > 0:
        print(f"Mapping usage rate: {total_replacements/total_mappings*100:.2f}%")

    # Display first few transformation examples
    print(f"\nFirst 5 transformation examples:")
    sample_count = 0
    for i in range(min(5, min_lines)):
        dict_record = dict_records[i]
        inp_record = inp_records[i]
        name_map = dict_record.get('name_map', {})
        original_method_name = inp_record.get('method_name', '')
        
        if name_map and original_method_name:
            transformed_method_name = apply_dictionary_replacement(original_method_name, name_map)
            if original_method_name != transformed_method_name:
                sample_count += 1
                print(f"  Example {sample_count}: '{original_method_name}' -> '{transformed_method_name}'")
                print(f"    Project: {inp_record.get('project', 'N/A')}")
                print(f"    File: {inp_record.get('file', 'N/A')}")
                print(f"    Dictionary: {dict(list(name_map.items())[:3])}{'...' if len(name_map) > 3 else ''}")

if __name__ == '__main__':
    main()