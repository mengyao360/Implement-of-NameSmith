import os
import sys
import pickle
import torch
import json
import random
import logging
import argparse
import numpy as np
from io import open
from functools import partial
from evaluation_utils import cal_scores
import networkx as nx
from torch_geometric.utils import from_networkx
from itertools import cycle
import torch.nn as nn
from include_verbs import best_t
from early_stopping import EarlyStopping
from peft import LoraConfig, get_peft_model
from tqdm import tqdm, trange
from CodeNamingModel import CodeNamingModel
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, Dataset, SequentialSampler, RandomSampler,TensorDataset
from torch.utils.data.distributed import DistributedSampler
from torch.optim import AdamW
from transformers import (WEIGHTS_NAME, get_linear_schedule_with_warmup,
                          RobertaConfig, RobertaModel, RobertaTokenizer, 
                          AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer)

MODEL_CLASSES = {
    'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer),
    'auto': (AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer)
}


logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)



logger = logging.getLogger(__name__)

class Example(object):

    def __init__(self, project, file, method_name, source_code, ast):
        self.project = project
        self.file = file
        self.method_name = method_name
        self.source_code = source_code
        self.ast = ast  # Abstract Syntax Tree

    def __repr__(self):
        return f"Example(project={self.project},\n file={self.file}, method_name={self.method_name},\n " \
               f"source_code={self.source_code},\n ast={self.ast}\n)"

def read_examples(filename):
    examples = []
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
       
            data = json.loads(line.strip())
            ast = data.get('ast', {})
            
            examples.append(Example(
                project=data.get('project', ''),
                file=data.get('file', ''),
                method_name=data.get('method_name', ''),
                source_code=data.get('source_code', ''),
                ast=ast,   
            ))
    return examples

class InputFeatures(object):
    def __init__(self, ast_source, ast_edge_index, target):
        self.ast_source = ast_source
        self.ast_edge_index = ast_edge_index
        self.target = target
    
    

def convert_examples_to_features(examples, tokenizer, args, stage=None):
    features = []
    max_source_length = args.max_source_length
    max_target_length = args.max_target_length

    for example in tqdm(examples, desc="Converting examples"):
        ast = example.ast
        target = example.method_name

        # Build graph
        ast_graph = nx.DiGraph()
        for node in ast["nodes"]:
            ast_graph.add_node(node["id"], label=node["label"])
        for edge in ast["edges"]:
            ast_graph.add_edge(edge["source"], edge["target"])

        # Tokenize node labels
        ast_labels = [node["label"] for node in ast["nodes"]]
        ast_source = tokenizer(
            ast_labels,
            padding="max_length",
            truncation=True,
            max_length=max_source_length,
            return_tensors="pt"
        )

        # Remove batch dim
        ast_source["input_ids"] = ast_source["input_ids"].squeeze(0)
        ast_source["attention_mask"] = ast_source["attention_mask"].squeeze(0)


        # Build edge index
        ast_edges = list(ast_graph.edges())
        if len(ast_edges) > 0:
            ast_edge_index = torch.tensor(ast_edges, dtype=torch.long).t().contiguous()
        else:
            ast_edge_index = torch.zeros((2, 0), dtype=torch.long)

        # Tokenize target
        target_tokens = tokenizer(
            target,
            padding="max_length",
            truncation=True,
            max_length=max_target_length,
            return_tensors="pt"
        )

        features.append(InputFeatures(
            ast_source=ast_source,
            ast_edge_index=ast_edge_index,
            target=target_tokens
        ))

    return features

class GraphDataset(Dataset):
    def __init__(self, examples, args):
        self.examples = examples
        self.args = args

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]
        ast_input_ids = example.ast_source["input_ids"]
        ast_attention_mask = example.ast_source["attention_mask"]
        ast_edge_index = example.ast_edge_index

        # Target: squeeze to [target_len]
        target_input_ids = example.target["input_ids"].squeeze(0)
        target_attention_mask = example.target["attention_mask"].squeeze(0)

        return {
            "input_ids": ast_input_ids,
            "attention_mask": ast_attention_mask,
            "edge_index": ast_edge_index,
            "target_input_ids": target_input_ids,
            "target_attention_mask": target_attention_mask,
        }

def graph_collate_fn(batch, tokenizer):
    node_lens = [item["input_ids"].shape[0] for item in batch]
    max_node_len = max(node_lens)
    seq_len = batch[0]["input_ids"].shape[1]

    input_ids_list = []
    attention_mask_list = []
    edge_index_list = []
    target_input_ids_list = []
    target_attention_mask_list = []

    for item in batch:
        node_len = item["input_ids"].shape[0]
        pad_nodes = max_node_len - node_len

        # Pad node-level input_ids and attention_mask
        if pad_nodes > 0:
            pad_ids = torch.full(
                (pad_nodes, seq_len),
                fill_value=item["input_ids"].new_full((), tokenizer.pad_token_id),
                dtype=item["input_ids"].dtype
            )
            pad_mask = torch.zeros(
                (pad_nodes, seq_len),
                dtype=item["attention_mask"].dtype
            )
            input_ids = torch.cat([item["input_ids"], pad_ids], dim=0)
            attn_mask = torch.cat([item["attention_mask"], pad_mask], dim=0)
        else:
            input_ids = item["input_ids"]
            attn_mask = item["attention_mask"]

        input_ids_list.append(input_ids)
        attention_mask_list.append(attn_mask)

        edge_len = item["edge_index"].shape[1]
        max_edge_len = max([b["edge_index"].shape[1] for b in batch])
        if edge_len < max_edge_len:
            pad_edges = torch.full(
                (2, max_edge_len - edge_len),
                fill_value=-1,
                dtype=item["edge_index"].dtype
            )
            edge_index_padded = torch.cat([item["edge_index"], pad_edges], dim=1)
        else:
            edge_index_padded = item["edge_index"]
        edge_index_list.append(edge_index_padded)

        target_input_ids_list.append(item["target_input_ids"])
        target_attention_mask_list.append(item["target_attention_mask"])

    batch_input_ids = torch.stack(input_ids_list)                # [B, N, L]
    batch_attention_mask = torch.stack(attention_mask_list)      # [B, N, L]
    batch_edge_index = torch.stack(edge_index_list)              # [B, 2, E]
    batch_target_input_ids = torch.stack(target_input_ids_list)  # [B, L_target]
    batch_target_attention_mask = torch.stack(target_attention_mask_list)  # [B, L_target]

    return (
        batch_input_ids,
        batch_attention_mask,
        batch_edge_index,
        batch_target_input_ids,
        batch_target_attention_mask,
    )

def set_seed(seed=42):
    random.seed(seed)
    os.environ['PYHTONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def main():
    parser = argparse.ArgumentParser()
    ## Required parameters  
    parser.add_argument("--model_type", default=None, type=str, required=True,
                        help="Model type: e.g. roberta")
    parser.add_argument("--model_name_or_path", default=None, type=str, required=True,
                        help="Path to pre-trained model: e.g. roberta-base" )   
    parser.add_argument("--output_dir", default=None, type=str, required=True,
                        help="The output directory where the model predictions and checkpoints will be written.")
    parser.add_argument("--load_model_path", default=None, type=str, 
                        help="Path to trained model: Should contain the .bin files" )    
    parser.add_argument("--load_training_state_path", type=str, default=None, help="Path to saved optimizer and scheduler")
    ## Other parameters
    parser.add_argument("--train_filename", default=None, type=str, 
                        help="The train filename. Should contain the .jsonl files for this task.")
    parser.add_argument("--dev_filename", default=None, type=str, 
                        help="The dev filename. Should contain the .jsonl files for this task.")
    parser.add_argument("--test_filename", default=None, type=str, 
                        help="The test filename. Should contain the .jsonl files for this task.")  

    parser.add_argument("--config_name", default="", type=str,
                        help="Pretrained config name or path if not the same as model_name")
    parser.add_argument("--tokenizer_name", default="", type=str,
                        help="Pretrained tokenizer name or path if not the same as model_name") 
    parser.add_argument("--max_node_length", default=2499, type=int,
                        help="The maximum total node length after tokenization. Sequences longer ")
    parser.add_argument("--max_source_length", default=64, type=int,
                        help="The maximum total source sequence length after tokenization. Sequences longer "
                             "than this will be truncated, sequences shorter will be padded.")
    parser.add_argument("--max_edge_length", default=2498, type=int,
                        help="The maximum total edge length after tokenization. Sequences longer ")
    parser.add_argument("--max_target_length", default=32, type=int,
                        help="The maximum total target sequence length after tokenization. Sequences longer "
                             "than this will be truncated, sequences shorter will be padded.")
    
    parser.add_argument("--do_train", action='store_true', help="")
    parser.add_argument("--do_eval", action='store_true',
                        help="Whether to run eval on the dev set.")
    parser.add_argument("--do_test", action='store_true',
                        help="Whether to run eval on the dev set.")
    parser.add_argument("--do_lower_case", action='store_true',
                        help="Set this flag if you are using an uncased model.")
    parser.add_argument("--no_cuda", action='store_true',
                        help="Avoid using CUDA when available") 
    
    parser.add_argument("--train_batch_size", default=8, type=int,
                        help="Batch size per GPU/CPU for training.")
    parser.add_argument("--eval_batch_size", default=8, type=int,
                        help="Batch size per GPU/CPU for evaluation.")
    parser.add_argument('--gradient_accumulation_steps', type=int, default=1,
                        help="Number of updates steps to accumulate before performing a backward/update pass.")
    parser.add_argument("--learning_rate", default=5e-5, type=float,
                        help="The initial learning rate for Adam.")
    parser.add_argument("--beam_size", default=10, type=int,
                        help="beam size for beam search")    
    parser.add_argument("--weight_decay", default=0.0, type=float,
                        help="Weight deay if we apply some.")
    parser.add_argument("--adam_epsilon", default=1e-8, type=float,
                        help="Epsilon for Adam optimizer.")
    parser.add_argument("--max_grad_norm", default=1.0, type=float,
                        help="Max gradient norm.")
    parser.add_argument("--num_train_epochs", default=3, type=int,
                        help="Total number of training epochs to perform.")
    parser.add_argument("--max_steps", default=-1, type=int,
                        help="If > 0: set total number of training steps to perform. Override num_train_epochs.")
    parser.add_argument("--eval_steps", default=-1, type=int,
                        help="")
    parser.add_argument("--train_steps", default=-1, type=int,
                        help="")
    parser.add_argument("--warmup_steps", default=0, type=int,
                        help="Linear warmup over warmup_steps.")
    parser.add_argument("--local_rank", type=int, default=-1,
                        help="For distributed training: local_rank")   
    parser.add_argument('--seed', type=int, default=42,
                        help="random seed for initialization")

    parser.add_argument("--start_epoch", type=int, default=0, help="Epoch to start training from")
    parser.add_argument("--include_verbs", action="store_true", help="Generate method names that include verbs")
    
    args = parser.parse_args()

    logger.info(args)

    logger.info("Process started. Current PID: %d", os.getpid())

    
    # os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.n_gpu = torch.cuda.device_count()
    args.device = device
    # Set seed
    set_seed(args.seed)
    
    # make dir if output_dir not exist
    if os.path.exists(args.output_dir) is False:
        os.makedirs(args.output_dir)

    lora_config = LoraConfig(
        r=8,  
        lora_alpha=16,  
        target_modules=["qkv_proj"],
        lora_dropout=0.1,  
    )
    
    config_class, model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
    config = config_class.from_pretrained(args.config_name, trust_remote_code=True)
    tokenizer = tokenizer_class.from_pretrained(args.tokenizer_name)
    encoder = model_class.from_pretrained(args.model_name_or_path, config=config, trust_remote_code=True)
    # encoder = get_peft_model(encoder, lora_config)
    decoder_layer = nn.TransformerDecoderLayer(d_model=config.hidden_size, nhead=config.num_attention_heads)
    decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
    model = CodeNamingModel(encoder=encoder,decoder=decoder,config=config,
                  beam_size=args.beam_size,max_length=args.max_target_length,
                  sos_id=tokenizer.cls_token_id,eos_id=tokenizer.sep_token_id)

    model = model.to(device)

    if args.load_model_path is not None:
        logger.info("reload model from {}".format(args.load_model_path))
        model.load_state_dict(torch.load(args.load_model_path))
    

    if args.n_gpu > 1:
        # multi-gpu training
        model = torch.nn.DataParallel(model)

    if args.do_train:
        # Prepare training data loader
        train_examples = read_examples(args.train_filename)
        train_features = convert_examples_to_features(train_examples, tokenizer, args, stage='train')
        train_data = GraphDataset(train_features, args)
        train_sampler = RandomSampler(train_data)
        train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=args.train_batch_size//args.gradient_accumulation_steps, num_workers=4, collate_fn=partial(graph_collate_fn, tokenizer=tokenizer))
        
        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
            'weight_decay': args.weight_decay},
            {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=len(train_dataloader)*args.num_train_epochs*0.1,num_training_steps=len(train_dataloader)*args.num_train_epochs)

        # load optimizer & scheduler state
        if args.load_training_state_path is not None:
            logger.info("reload optimizer and scheduler from {}".format(args.load_training_state_path))
            training_state = torch.load(args.load_training_state_path)
            optimizer.load_state_dict(training_state['optimizer_state_dict'])
            scheduler.load_state_dict(training_state['scheduler_state_dict'])

        #Start training
        logger.info("***** Running training *****")
        logger.info("  Num examples = %d", len(train_examples))
        logger.info("  Batch size = %d", args.train_batch_size)
        logger.info("  Num epoch = %d", args.num_train_epochs)
        logger.info("  " + "*" * 20)

        model.train()
        dev_dataset={}
        early_stopping = EarlyStopping(patience=5, delta=1e-4)
        nb_tr_examples,nb_tr_steps,tr_loss,global_step,best_bleu,best_rouge,best_loss = 0,0,0,0,0,0,1e6
        # for epoch in range(args.start_epoch, args.num_train_epochs):
        for epoch in range(args.num_train_epochs):
            bar = tqdm(train_dataloader,total=len(train_dataloader))
            for batch in bar:
                batch = tuple(t.to(device) for t in batch)
                ast_ids, ast_mask, ast_edge_index, target_ids, target_mask = batch
                _,loss = model(ast_ids, ast_mask, ast_edge_index, target_ids, target_mask)
                if args.n_gpu > 1:
                    loss = loss.mean() # mean() to average on multi-gpu.
                if args.gradient_accumulation_steps > 1:
                    loss = loss / args.gradient_accumulation_steps

                tr_loss += loss.item()
                train_loss=round(tr_loss*args.gradient_accumulation_steps/(nb_tr_steps+1),4)
                bar.set_description("epoch {} loss {}".format(epoch,train_loss))
                nb_tr_examples += ast_ids.size(0)
                nb_tr_steps += 1
                loss.backward()
                if (nb_tr_steps + 1) % args.gradient_accumulation_steps == 0:
                    #Update parameters
                    optimizer.step()
                    optimizer.zero_grad()
                    scheduler.step()
                    global_step += 1

            # save last optimizer & scheduler satate
            last_training_state_dir = os.path.join(args.output_dir, 'checkpoint-training-state-last')
            if not os.path.exists(last_training_state_dir):
                os.makedirs(last_training_state_dir)
            output_training_state_file = os.path.join(last_training_state_dir, "training_state.bin")
            torch.save({
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict()
            }, output_training_state_file)
            logger.info("Save the optimizer and scheduler into %s", output_training_state_file)
            logger.info("  " + "*" * 20)

            eval_loss, batch_num = 0, 0
            # if args.do_eval and epoch in [ int(args.num_train_epochs*(i+1)//20) for i in range(20)]:
            if args.do_eval:
                tr_loss = 0
                nb_tr_examples, nb_tr_steps = 0, 0                     
                if 'dev_loss' in dev_dataset:
                    eval_examples,eval_data=dev_dataset['dev_loss']
                else:
                    eval_examples = read_examples(args.dev_filename)
                    eval_features = convert_examples_to_features(eval_examples, tokenizer, args, stage='dev') 
                    eval_data = GraphDataset(eval_features, args)
                    dev_dataset['dev_loss']=eval_examples,eval_data
                eval_sampler = SequentialSampler(eval_data)
                eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.eval_batch_size, num_workers=4, collate_fn=partial(graph_collate_fn, tokenizer=tokenizer))

                logger.info("***** Running evaluation *****")
                logger.info("  Num examples = %d", len(eval_examples))
                logger.info("  Batch size = %d", args.eval_batch_size)

                #Start Evaling model
                model.eval()
                eval_loss, batch_num = 0, 0
                for batch in eval_dataloader:
                    batch = tuple(t.to(device) for t in batch)           
                    ast_ids, ast_mask, ast_edge_index, target_ids, target_mask = batch
                    with torch.no_grad():
                        logits, loss= model(ast_ids, ast_mask, ast_edge_index, target_ids, target_mask)     
                    eval_loss += loss.sum().item()
                    batch_num += 1
                eval_loss = eval_loss / batch_num
                eval_ppl = round(np.exp(eval_loss), 5)
                result = {'eval_ppl': eval_ppl,
                        'global_step': global_step+1,
                        'train_loss': round(train_loss,5)}
                for key in sorted(result.keys()):
                    logger.info("  %s = %s", key, str(result[key]))
                
                early_stopping(eval_loss)
                if early_stopping.early_stop:
                    logger.info("Early stopping")
                    break
                
                # save last checkpoint
                last_output_dir = os.path.join(args.output_dir, 'checkpoint-last')
                if not os.path.exists(last_output_dir):
                    os.makedirs(last_output_dir)
                model_to_save = model.module if hasattr(model, 'module') else model
                output_model_file = os.path.join(last_output_dir, "pytorch_model.bin")
                torch.save(model_to_save.state_dict(), output_model_file)
                logger.info("Save the last model into %s", output_model_file)
                logger.info("  "+"*"*20)  
                
                if eval_loss < best_loss:
                    logger.info("  Best ppl:%s", eval_ppl)
                    best_loss = eval_loss

                    # Save best checkpoint for best ppl
                    output_dir = os.path.join(args.output_dir, 'checkpoint-best-ppl')
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    model_to_save = model.module if hasattr(model, 'module') else model
                    output_model_file = os.path.join(output_dir, "pytorch_model.bin")
                    torch.save(model_to_save.state_dict(), output_model_file)
                    logger.info("Save the best ppl model into %s", output_model_file)
                    logger.info("  " + "*" * 20)
                
                #Calculate rouge and bleu
                if 'dev_loss' in dev_dataset:
                    eval_examples,eval_data=dev_dataset['dev_loss']
                else:
                    eval_examples = read_examples(args.dev_filename)
                    eval_features = convert_examples_to_features(eval_examples, tokenizer, args, stage='dev') 
                    eval_data = GraphDataset(eval_features, args)
                    dev_dataset['dev_loss']=eval_examples,eval_data
                eval_sampler = SequentialSampler(eval_data)
                eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.eval_batch_size, num_workers=4, collate_fn=partial(graph_collate_fn, tokenizer=tokenizer))
                model.eval()
                p=[]
                for batch in eval_dataloader:
                    batch = tuple(t.to(device) for t in batch)           
                    ast_ids, ast_mask, ast_edge_index, target_ids, target_mask = batch
                    with torch.no_grad():
                        preds = model(ast_ids, ast_mask, ast_edge_index)
                        for pred in preds:
                            t=pred[0].cpu().numpy()
                            t=list(t)
                            if 0 in t:
                                t=t[:t.index(0)]
                            text = tokenizer.decode(t,clean_up_tokenization_spaces=False)
                            p.append(text)  
                model.train()
                predictions=[]
                accs=[]
                with open(os.path.join(args.output_dir,"dev.output"),'w') as f, open(os.path.join(args.output_dir,"dev.gold"),'w') as f1:
                    for ref,gold in zip(p,eval_examples):
                        predictions.append(ref)
                        f.write(ref+'\n')
                        f1.write(gold.method_name+'\n')     
                        accs.append(ref==gold.method_name)
                
                bleu, _, _, _, _, rouge1, rouge2, rougel, _, _, _ = cal_scores(tokenizer, os.path.join(args.output_dir, "dev.gold"), os.path.join(args.output_dir, "dev.output"))
                logger.info("BLEU: %s", bleu)
                logger.info("ROUGE-1: %s", rouge1)
                logger.info("ROUGE-2: %s", rouge2)
                logger.info("ROUGE-L: %s", rougel)
                logger.info("  "+"*"*20)
                # Save best checkpoint for best bleu
                if bleu > best_bleu:
                    logger.info("  Best Bleu:%s", bleu)
                    best_bleu = bleu
                    # Save best checkpoint for best bleu
                    output_dir = os.path.join(args.output_dir, 'checkpoint-best-Bleu')
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    model_to_save = model.module if hasattr(model, 'module') else model
                    output_model_file = os.path.join(output_dir, "pytorch_model.bin")
                    torch.save(model_to_save.state_dict(), output_model_file)
                    logger.info("Save the best Bleu model into %s", output_model_file)
                
                if rouge1 > best_rouge:
                    logger.info("  Best Rouge:%s", rouge1)
                    best_rouge = rouge1
                    # Save best checkpoint for best rouge
                    output_dir = os.path.join(args.output_dir, 'checkpoint-best-Rouge')
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    model_to_save = model.module if hasattr(model, 'module') else model
                    output_model_file = os.path.join(output_dir, "pytorch_model.bin")
                    torch.save(model_to_save.state_dict(), output_model_file)
                    logger.info("Save the best Rouge model into %s", output_model_file)

                # logger.info("***** CUDA.empty_cache() *****")
                # torch.cuda.empty_cache()

    if args.do_test:
        files=[]
        if args.test_filename is not None:
            files.append(args.test_filename)
        for idx,file in enumerate(files):  
            logger.info("Test file: {}".format(file))
            eval_examples = read_examples(file)
            eval_features = convert_examples_to_features(eval_examples, tokenizer, args, stage='test')
            eval_data = GraphDataset(eval_features,args) 

            eval_sampler = SequentialSampler(eval_data)
            eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.eval_batch_size, num_workers=4, collate_fn=partial(graph_collate_fn, tokenizer=tokenizer))
            
            model.eval() 
            p=[]
            for batch in tqdm(eval_dataloader,total=len(eval_dataloader)):
                batch = tuple(t.to(device) for t in batch)
                ast_ids, ast_mask, ast_edge_index, target_ids, target_mask = batch        
                with torch.no_grad():
                    preds = model(ast_ids, ast_mask, ast_edge_index)  
                    for pred in preds:
                        if args.include_verbs:
                            t = best_t(pred, tokenizer) 
                        else:
                            t = pred[0].cpu().numpy().tolist()
                            if 0 in t:
                                t = t[:t.index(0)]
                        t = list(t)
                        if 0 in t:
                            t = t[:t.index(0)]
                        text = tokenizer.decode(t,clean_up_tokenization_spaces=False)
                        p.append(text)
            model.train()
            predictions=[]
            accs=[]
            pred_file = os.path.join(args.output_dir, "test_{}.output".format(str(idx)))
            gold_file = os.path.join(args.output_dir, "test_{}.gold".format(str(idx)))

            with open(pred_file, 'w') as f, open(gold_file, 'w') as f1:
                for ref, gold in zip(p, eval_examples):
                    predictions.append(ref)
                    f.write(ref + '\n')
                    f1.write(gold.method_name + '\n')
                    accs.append(ref == gold.method_name)

            bleu, bleu1, bleu2, bleu3, bleu4, rouge1, rouge2, rougel, precision, recall, f1 = cal_scores(tokenizer, gold_file, pred_file)
            logger.info("  xMatch = %s " % (str(round(np.mean(accs) * 100, 4))))
            logger.info("  BLEU   = %.4f" % bleu)
            logger.info("  BLEU-1   = %.4f" % bleu1)
            logger.info("  BLEU-2   = %.4f" % bleu2)
            logger.info("  BLEU-3   = %.4f" % bleu3)
            logger.info("  BLEU-4   = %.4f" % bleu4)
            logger.info("  ROUGE-1= %.4f" % rouge1)
            logger.info("  ROUGE-2= %.4f" % rouge2)
            logger.info("  ROUGE-L= %.4f" % rougel)
            logger.info("  Precision = %.4f" % precision)
            logger.info("  Recall    = %.4f" % recall)
            logger.info("  F1        = %.4f" % f1)
            logger.info("  " + "=" * 20)



if __name__ == "__main__":
    main()



