# NameSmith

Research implementation and replication package accompanying **"Developer-Guided Action-Oriented Java Method Name Generation via Statement-Level Semantic and Structural Modeling"** by Yao Meng, Xin Chen, Yanming Yang, and Zhiyang Zhou.

NameSmith predicts Java method names from code by combining code-structure understanding with developer naming conventions. This repository contains the data preprocessing, graph generator, GraphCodeBERT-based training/evaluation code, and LLM baseline evaluation scripts used in the paper.

## Overview

NameSmith uses statement-level AST graphs extracted with Tree-sitter. The processed examples are stored as JSONL records containing the project/file metadata, original method name, source code, AST. The model is trained to generate method names from this structured representation.

The dataset follows the same repository pool used by [MNire](https://dl.acm.org/doi/pdf/10.1145/3377811.3380926), [Code2vec](https://arxiv.org/pdf/1803.09473.pdf), and [DeepName](https://arxiv.org/pdf/2103.00269.pdf). The repository list is provided in [`data/repos.txt`](data/repos.txt). In our experiments, we selected 1,000 Java projects, collected more than 1.5M qualified methods, and split them into training, validation, and test sets with an 8:1:1 ratio.

The processed train/validation/test splits are included as compressed archive parts under `data/archives/`. After cloning, restore the original JSONL files before running training or evaluation:

```bash
python3 scripts/restore_data.py
```

The restore script requires only Python 3 and verifies archive and output checksums. See [`data/README.md`](data/README.md) for details. It produces:

| File | Purpose |
| --- | --- |
| `data/train.jsonl` | Training set. |
| `data/val.jsonl` | Validation set. |
| `data/test.jsonl` | Test set. |

## Repository Structure

| Path | Description |
| --- | --- |
| `graph_generator/` | Builds statement-level AST representations from Java source files. |
| `data/` | Ready-to-use split dataset and the source repository list. |
| `processed_code2vec_data/` | Scripts for filtering, splitting, and constructing RQ4 data. Regenerated JSONL files can be written here. |
| `model/` | NameSmith model, training loop, decoding, and evaluation utilities. |
| `eval_LLM/` | Prompt-based LLM baseline inference and evaluation scripts. |
| `scripts/restore_data.py` | Restores and verifies the original dataset from compressed archive parts. |
| `empircal.xlsx` | Experimental result workbook. |
| `requirements.txt` | Installation command checklist. Some packages need CUDA/PyTorch-specific wheels. |

## Environment Setup

Create and activate a Python environment first:

Install the core dependencies:

```bash
python -m pip install tree-sitter==0.21.3
python -m pip install jsonlines tqdm networkx graphviz spacy
python -m pip install transformers peft scikit-learn sacrebleu rouge-score
python -m pip install torch torchvision torchaudio
python -m pip install torch_geometric
```

Install the spaCy English model from the wheel included in this repository:

```bash
python -m pip install model/en_core_web_sm-3.8.0-py3-none-any.whl
```

If you use PyTorch Geometric with CUDA, install the matching extension wheels for your local PyTorch/CUDA version. For example, the current command checklist uses the PyTorch 2.7.0 + CUDA 12.6 wheel index:

```bash
python -m pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv \
  -f https://data.pyg.org/whl/torch-2.7.0+cu126.html
```

## Tree-Sitter Java Grammar

The graph generator expects the Java grammar under `treesitter_envs/vendor/tree-sitter-java` and builds the parser library at runtime.

```bash
mkdir -p treesitter_envs/vendor treesitter_envs/build
git clone https://github.com/tree-sitter/tree-sitter-java.git treesitter_envs/vendor/tree-sitter-java
```

## Dataset

The NameSmith training/evaluation commands and the LLM baseline testing commands use the processed dataset already provided in `data/`:

Run `python3 scripts/restore_data.py` from the repository root first to unpack the distributed archives.

```text
data/train.jsonl
data/val.jsonl
data/test.jsonl
```

## Rebuilding the Dataset

You only need this section if you want to regenerate the processed JSONL files from raw Java projects.

Place the raw Java projects under:

```text
data/code2vecdataset/
  project_1/
    **/*.java
  project_2/
    **/*.java
```

Then generate graph records:

```bash
python graph_generator/main.py \
  --inputpath data/code2vecdataset \
  --outputpath processed_code2vec_data \
  --type ast cfg \
  --format jsonl
```

This creates:

```text
processed_code2vec_data/data.jsonl
```

Next, filter examples and split the data:

```bash
python processed_code2vec_data/dataProcessor.py
python processed_code2vec_data/dataProcessor2.py
python processed_code2vec_data/dataSeparater.py
```

The preprocessing scripts currently use hard-coded file paths near the top of each file. Before running them, confirm that the input/output paths point to your local repository, for example:

```text
processed_code2vec_data/data.jsonl
processed_code2vec_data/data_with_verbs.jsonl
processed_code2vec_data/data_with_verbs_less_100.jsonl
processed_code2vec_data/train.jsonl
processed_code2vec_data/test.jsonl
processed_code2vec_data/val.jsonl
```

The regenerated split files are:

| File | Purpose |
| --- | --- |
| `processed_code2vec_data/train.jsonl` | Training set. |
| `processed_code2vec_data/val.jsonl` | Validation set. |
| `processed_code2vec_data/test.jsonl` | Test set. |

If you want the regenerated files to become the default dataset, copy them into `data/` or update the NameSmith training/evaluation and LLM testing paths below.

## RQ4 Data Construction

RQ4 evaluates how developer naming conventions affect method-name generation. The RQ4 scripts replace selected identifiers in the source code/AST and then apply the same replacement dictionary to method names.

For each split, edit the three variables in `processed_code2vec_data/built_data_for_rq4.py`. The example below uses the ready-to-use training split in `data/` and writes the transformed files to `processed_code2vec_data/`:

```python
inp = 'data/train.jsonl'
out = 'processed_code2vec_data/train_transformed_rq4.jsonl'
name_map_file = 'processed_code2vec_data/train_dict_rq4.jsonl'
```

Run the builder:

```bash
python processed_code2vec_data/built_data_for_rq4.py
```

Then apply the dictionary to the target method names:

```bash
python processed_code2vec_data/dict-based_json_string_replacement_for_rq4.py \
  --dict_file processed_code2vec_data/train_dict_rq4.jsonl \
  --inp_file processed_code2vec_data/train_transformed_rq4.jsonl \
  --out_file processed_code2vec_data/train_data_rq4.jsonl
```

Repeat the same process for `test.jsonl` and `val.jsonl`, changing the file prefixes accordingly.

## Model Training

The shell scripts in `model/` are templates. Check the dataset paths, checkpoint directory, batch size, and pretrained model path before launching a run.

Example training command:

```bash
cd model

python run.py \
  --do_train \
  --do_eval \
  --model_type roberta \
  --model_name_or_path graphcodebert-base \
  --tokenizer_name graphcodebert-base \
  --config_name graphcodebert-base \
  --train_filename ../data/train.jsonl \
  --dev_filename ../data/val.jsonl \
  --output_dir ../saved_models/namesmith \
  --max_source_length 64 \
  --max_target_length 16 \
  --beam_size 10 \
  --train_batch_size 32 \
  --eval_batch_size 32 \
  --learning_rate 1e-5 \
  --num_train_epochs 10
```

## Model Testing

Evaluate the best checkpoint on the test set:

```bash
cd model

python run.py \
  --do_test \
  --model_type roberta \
  --model_name_or_path graphcodebert-base \
  --tokenizer_name graphcodebert-base \
  --config_name graphcodebert-base \
  --load_model_path ../saved_models/namesmith/checkpoint-best-ppl/pytorch_model.bin \
  --test_filename ../data/test.jsonl \
  --output_dir ../saved_models/namesmith \
  --max_source_length 64 \
  --max_target_length 16 \
  --beam_size 10 \
  --eval_batch_size 128
```

Compute BLEU, ROUGE, precision, recall, and F1:

```bash
cd model

python evaluation_utils_test.py \
  --tokenizer_path graphcodebert-base \
  --gold_file ../saved_models/namesmith/test_0.gold \
  --pred_file ../saved_models/namesmith/test_0.output
```

## LLM Baseline Evaluation

The `eval_LLM/` directory contains prompt-based testing scripts for causal LLM baselines such as Llama, CodeLlama, and StarCoder2. These scripts do not train or fine-tune the LLMs; they load pretrained models, run inference on the test split, and compute evaluation metrics.

DeepSeek and Qwen use separate model-specific code because their loading, inference, and evaluation settings differ from the generic script shown below. Use `eval_LLM/deepkseek_generate_name.py` and `eval_LLM/qwen_generate_name.py` for generation, and `eval_LLM/eval_qwen_deepseek.py` for evaluation. They use the same metric definitions as the other LLM baselines.

All three generation scripts contain the same fixed 12-example prompt in `PROMPT_TEMPLATE`. The demonstrations can be found in the training split and stay fixed for all queries. Regenerate predictions when changing the prompt or inference settings. Pretrained checkpoints and generated LLM predictions are not included in this package.

Example:

```bash
cd eval_LLM

python run.py \
  --test_data_path ../data/test.jsonl \
  --output_file_path outputs/StarCoder2-15b_rq3.jsonl \
  --load_model_path /path/to/StarCoder2 \
  --batch_size 32 \
  --max_length 2048 \
  --max_new_tokens 16
```

After generation, update `eval_LLM/eval.py` to point to the generated JSONL file and run it to create `.gold` and `.output` files:

```bash
python eval.py
```

Then evaluate:

```bash
python evaluation_utils_test.py \
  --tokenizer_path /path/to/graphcodebert_tokenizer \
  --gold_file outputs/StarCoder2-15b_rq3.gold \
  --pred_file outputs/StarCoder2-15b_rq3.output
```

## Citation

The replication package is available at <https://github.com/mengyao360/Implement-of-NameSmith>.
Citation metadata for the software is provided in [`CITATION.cff`](CITATION.cff).
The accompanying paper is titled **"Developer-Guided Action-Oriented Java Method Name Generation via Statement-Level Semantic and Structural Modeling"**.
Final publication details and a paper DOI will be added when available.

## Third-party Materials

The dataset contains Java source excerpts from upstream repositories listed in
`data/repos.txt`. Their original licenses and attribution requirements continue to
apply. The bundled spaCy model wheels are third-party distributions. This package
does not relicense those materials.
