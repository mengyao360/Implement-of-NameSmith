import re
import jsonlines

input_file_path = "processed_code2vec_data/data_with_verbs.jsonl"
output_file_path = "processed_code2vec_data/data_with_verbs_less_100.jsonl"

with jsonlines.open(input_file_path, "r") as reader, jsonlines.open(output_file_path, "w") as writer:
    total = 0
    processed = 0
    for obj in reader:
        total += 1
        ast_nodes_count = len(obj.get('ast', {}).get('nodes', []))

        if ast_nodes_count <= 100:
            processed += 1
            writer.write(obj)

    print(f'total:{total}')
    print(f'processed:{processed}')
