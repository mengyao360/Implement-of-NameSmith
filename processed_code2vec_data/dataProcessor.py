import re
import jsonlines
import spacy

nlp = spacy.load("en_core_web_sm")

def split_identifier(identifier):
    parts = identifier.split('_')
    
    split_parts = []
    for part in parts:
        camel_split = re.sub(r'([a-z])([A-Z])', r'\1 \2', part)

        doc = nlp(camel_split)
        split_parts.extend([token.text for token in doc])

    return " ".join(split_parts)

input_file_path = "/processed_code2vec_data/data.jsonl"
output_file_path = "/processed_code2vec_data/data_with_verbs.jsonl"

with jsonlines.open(input_file_path, "r") as reader, jsonlines.open(output_file_path, "w") as writer:
    total = 0
    processed = 0
    for obj in reader:
        if "method_name" in obj:
            total+=1
            method_name = obj["method_name"]
            processed_name = split_identifier(method_name)

            doc = nlp(processed_name)
            pos_tags = [(token.text, token.pos_) for token in doc]

            if any(pos == "VERB" for _, pos in pos_tags):
                print(pos_tags)
                processed+=1
                writer.write(obj)

    print(f'total:{total}')
    print(f'processed:{processed}')
