#!/bin/bash

OUTPUT_FILE="evaluation_results.txt"


> "$OUTPUT_FILE"


log_and_print() {
    echo "$1" | tee -a "$OUTPUT_FILE"
}


run_evaluation() {
    local title="$1"
    local gold_file="$2"
    local pred_file="$3"
    local tokenizer_path="$4"
    
    log_and_print ""
    log_and_print "=========================================="
    log_and_print "$title"
    log_and_print "=========================================="
    log_and_print "Gold file: $gold_file"
    log_and_print "Pred file: $pred_file"
    log_and_print ""
    
    python evaluation_utils_test.py \
        --tokenizer_path "$tokenizer_path" \
        --gold_file "$gold_file" \
        --pred_file "$pred_file" | tee -a "$OUTPUT_FILE"
}

log_and_print "Evaluation started at: $(date)"
log_and_print ""

log_and_print "Length: 16"

run_evaluation \
    "RQ3: No verbs Llama3-8B" \
    "eval_LLM/Llama-3.1-8B-Instruct/rq3/Llama3-8b_rq3.gold" \
    "eval_LLM/Llama-3.1-8B-Instruct/rq3/Llama3-8b_rq3.output"\
    "llama3"

run_evaluation \
    "RQ3: No verbs CodeLlama-13B" \
    "eval_LLM/CodeLlama-13b-Instruct-hf/rq3/CodeLlama-13b_rq3.gold" \
    "eval_LLM/CodeLlama-13b-Instruct-hf/rq3/CodeLlama-13b_rq3.output"\
    "CodeLlama-13b-Instruct-hf"

run_evaluation \
    "RQ3: No verbs StarCoder2-15B" \
    "eval_LLM/StarCoder2-15b/rq3/starcoder2-15b_rq3.gold" \
    "eval_LLM/StarCoder2-15b/rq3/starcoder2-15b_rq3.output"\
    "StarCoder2"
    
# RQ4: include verbs
run_evaluation \
    "RQ4: include verbs Llama3-8B" \
    "saved_models_round7/test_0.gold_transformed" \
    "eval_LLM/Llama-3.1-8B-Instruct/rq4/Llama3-8b_rq4.output"\
    "llama3"

run_evaluation \
    "RQ4: include verbs CodeLlama-13B" \
    "saved_models_round7/test_0.gold_transformed" \
    "eval_LLM/CodeLlama-13b-Instruct-hf/rq4/CodeLlama-13b_rq4.output"\
    "CodeLlama-13b-Instruct-hf"

run_evaluation \
    "RQ4: include verbs StarCoder2-15B" \
    "saved_models_round7/test_0.gold_transformed" \
    "eval_LLM/StarCoder2-15b/rq4/starcoder2-15b_rq4.output"\
    "StarCoder2"

log_and_print ""
log_and_print "Evaluation completed at: $(date)"
log_and_print "Results saved to: $OUTPUT_FILE"