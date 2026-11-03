import json

def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line.strip())

def main():
    input_file = 'processed_code2vec_data/v3/train.jsonl'
    output_file = 'processed_code2vec_data/v3/train.gold'

    method_names = []
    processed_count = 0

    for record in read_jsonl(input_file):
        method_name = record.get('method_name', '')
        method_names.append(method_name)
        processed_count += 1

        if processed_count % 1000 == 0:
            print(f"already {processed_count} lines")

    print(f"write method_name to file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for method_name in method_names:
            f.write(method_name + '\n')
    
    print(f"total {processed_count} ")
    print(f"save in : {output_file}")
    
    print(f"\n top 5:")
    for i in range(min(5, len(method_names))):
        print(f"  {i+1}: {method_names[i]}")

if __name__ == '__main__':
    main()