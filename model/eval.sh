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
    
    log_and_print ""
    log_and_print "=========================================="
    log_and_print "$title"
    log_and_print "=========================================="
    log_and_print "Gold file: $gold_file"
    log_and_print "Pred file: $pred_file"
    log_and_print ""
    
    python evaluation_utils_test.py \
        --tokenizer_path "graphcodebert-base" \
        --gold_file "$gold_file" \
        --pred_file "$pred_file" | tee -a "$OUTPUT_FILE"
}

log_and_print "Evaluation started at: $(date)"
log_and_print ""

# Length: 16
log_and_print "Length: 16"

# RQ3: No verbs
# run_evaluation \
#     "RQ3: No verbs" \
#     "saved_models_round7/target_length_16/test_no_verb_ppl/test_0.gold" \
#     "saved_models_round7/target_length_16/test_no_verb_ppl/test_0.output"

# # RQ3: include verbs
# run_evaluation \
#     "RQ3: include verbs" \
#     "saved_models_round7/target_length_16/test_with_verb_ppl/test_0.gold" \
#     "saved_models_round7/target_length_16/test_with_verb_ppl/test_0.output"

# RQ4: No verbs
run_evaluation \
    "RQ4: No verbs" \
    "saved_models_round8/test_0.gold_transformed" \
    "saved_models_round8/target_length_16/test_no_verb_ppl_rq4/test_0.output"

# # RQ4: include verbs
# run_evaluation \
#     "RQ4: include verbs" \
#     "saved_models_round8/test_0.gold_transformed" \
#     "saved_models_round8/target_length_16/test_with_verb_ppl_rq4/test_0.output"

log_and_print ""
log_and_print "Evaluation completed at: $(date)"
log_and_print "Results saved to: $OUTPUT_FILE"