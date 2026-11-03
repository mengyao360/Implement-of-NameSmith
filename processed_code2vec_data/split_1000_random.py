import os
import shutil
import random

source_dir = "processed_code2vec_data/1000_random"

target_dir = "processed_code2vec_data/split_1000_random"

operation = "copy" 

train_dir = os.path.join(target_dir, "training")
val_dir = os.path.join(target_dir, "val")
test_dir = os.path.join(target_dir, "test")

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

all_projects = [f for f in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, f))]
random.shuffle(all_projects)  

total = len(all_projects)
train_count = int(total * 0.8)
val_count = int(total * 0.1)
test_count = total - train_count - val_count

train_projects = all_projects[:train_count]
val_projects = all_projects[train_count:train_count + val_count]
test_projects = all_projects[train_count + val_count:]

def transfer_projects(projects, dest_dir, op):
    for project in projects:
        src_path = os.path.join(source_dir, project)
        dst_path = os.path.join(dest_dir, project)
        if op == "copy":
            shutil.copytree(src_path, dst_path)
            print(f" Copied {project} -> {dest_dir}")
        elif op == "move":
            shutil.move(src_path, dst_path)
            print(f" Moved {project} -> {dest_dir}")
        else:
            raise ValueError(" 'copy' or 'move'")


transfer_projects(train_projects, train_dir, operation)
transfer_projects(val_projects, val_dir, operation)
transfer_projects(test_projects, test_dir, operation)

print(f"Training: {train_count} ")
print(f"Validation: {val_count} ")
print(f"Test: {test_count} ")
