batch_size=32
# mode_name=Llama-3.1-8B-Instruct
# mode_name=CodeLlama-13b-Instruct-hf
# mode_name=Llama-4-Scout-17B-16E-Instruct
mode_name=StarCoder2-15b

# save_name=Llama3-8b_rq3.jsonl
save_name=StarCoder2-15b_rq4.jsonl
# save_name=CodeLlama-13b_rq3.jsonl
# save_name=Llama4-17b_rq3.jsonl


output_dir=coderead/eval_LLM/$mode_name

test_file=processed_code2vec_data/v3/test_transformed_rq4.jsonl
# test_file=processed_code2vec_data/v3/test.jsonl

pretrained_model=StarCoder2/
# pretrained_model=llama3
# pretrained_model=CodeLlama-13b-Instruct-hf


mkdir -p $output_dir
CUDA_VISIBLE_DEVICES=4 python run.py \
--test_data_path $test_file \
--output_file_path $output_dir/$save_name \
--load_model_path  $pretrained_model \
--batch_size $batch_size \
--max_length 2048 \
--max_new_tokens 16 2>&1| tee $output_dir/eval_rq4.log
