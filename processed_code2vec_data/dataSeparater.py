import jsonlines
import spacy
import random
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")

input_file_path = "processed_code2vec_data/data_with_verbs_less_100.jsonl"
train_file_path = "processed_code2vec_data/train.jsonl"
test_file_path = "processed_code2vec_data/test.jsonl"
val_file_path = "processed_code2vec_data/val.jsonl"

print("method_name lines...")
valid_indices = []
with jsonlines.open(input_file_path, "r") as reader:
    for idx, obj in enumerate(reader):
        if "method_name" in obj:
            valid_indices.append(idx)

total_valid = len(valid_indices)
print(f"total: {total_valid}")


train_count = int(total_valid * 0.8)
test_count = int(total_valid * 0.1)
val_count = total_valid - train_count - test_count 

random.seed(42)
random.shuffle(valid_indices)

train_indices = set(valid_indices[:train_count])
test_indices = set(valid_indices[train_count:train_count + test_count])
val_indices = set(valid_indices[train_count + test_count:])

print("spliting ...")
min_length = float('inf')
max_length = float('-inf')
train_written = test_written = val_written = 0

with jsonlines.open(input_file_path, "r") as reader, \
     jsonlines.open(train_file_path, "w") as train_writer, \
     jsonlines.open(test_file_path, "w") as test_writer, \
     jsonlines.open(val_file_path, "w") as val_writer:

    for idx, obj in enumerate(tqdm(reader, desc="process data")):
        if idx in train_indices:
            train_writer.write(obj)
            train_written += 1
        elif idx in test_indices:
            test_writer.write(obj)
            test_written += 1
        elif idx in val_indices:
            val_writer.write(obj)
            val_written += 1
        else:
            continue

        if "method_name" in obj:
            tokens = [token.text for token in nlp(obj["method_name"])]
            l = len(tokens)
            min_length = min(min_length, l)
            max_length = max(max_length, l)


print(f"total: {total_valid}")
print(f"train_written: {train_written}")
print(f"test_written: {test_written}")
print(f"val_written: {val_written}")
print(f"name length - min: {min_length}, max: {max_length}")
