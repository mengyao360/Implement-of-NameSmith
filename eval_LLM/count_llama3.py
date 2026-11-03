file_path = "eval_LLM/Llama-3.1-8B-Instruct/rq3/Llama3-8b_rq3.output"

non_empty_count = 0
total_count = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        total_count += 1
        if line.strip():  
            non_empty_count += 1

if total_count > 0:
    ratio = non_empty_count / total_count
else:
    ratio = 0

print(f"total_count: {total_count}")
print(f"non_empty_count: {non_empty_count}")
print(f"ratio: {ratio:.4f}")
print(f"1-ratio: {1-ratio:.4f}")
