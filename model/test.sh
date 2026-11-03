batch_size=128
beam_size=10
source_length=64
target_length=16
output_dir=saved_models_round1
test_file=processed_code2vec_data/test.jsonl
load_model_path=$output_dir/checkpoint-best-ppl/pytorch_model.bin 
pretrained_model=graphcodebert-base

python run.py \
--do_test \
--model_type roberta \
--model_name_or_path $pretrained_model \
--tokenizer_name graphcodebert-base \
--config_name graphcodebert-base \
--load_model_path $load_model_path \
--test_filename $test_file \
--output_dir $output_dir \
--max_source_length $source_length \
--max_target_length $target_length \
--beam_size $beam_size \
--eval_batch_size $batch_size 2>&1| tee $output_dir/test_rq1.log