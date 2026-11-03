import os
import argparse
import json
import torch
import logging
import re
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("Eval")


METHOD_BODY_PLACEHOLDER = "__METHOD_BODY__"


PROMPT_TEMPLATE = """Similar Examples:
Example 1:
Method Body: {
java.text.SimpleDateFormat formater = new java.text.SimpleDateFormat(
        "MM");
String cur_month = formater.format(date);
return cur_month;
}
Method Name: getMonth

Example 2:
Method Body: {
return sql("select uuid from HostVO where uuid = :uuid", String.class).param("uuid", uuid).find();
}
Method Name: findHostByUuid

Example 3:
Method Body: {
if (resourceExistsSet.contains(path)) {
    return true;
}
if (Files.exists(resourceRoot.resolve(path))) {
    resourceExistsSet.add(path);
    return true;
} else {
    return false;
}
}
Method Name: resourceExists

Example 4:
Method Body: {
super.onActivityCreated(savedInstanceState);
}
Method Name: onActivityCreated

Example 5:
Method Body: {
Map<String, String> responseHeaders = RateLimitingPolicy.responseHeaders(config, rtr,
        defaultLimitHeader(), defaultRemainingHeader(), defaultResetHeader());

IPolicyFailureFactoryComponent failureFactory = context.getComponent(IPolicyFailureFactoryComponent.class);
PolicyFailure failure = limitExceededFailure(failureFactory);
failure.getHeaders().putAll(responseHeaders);
chain.doFailure(failure);
}
Method Name: doQuotaExceededFailure

Example 6:
Method Body: {
if (permissions == null) {
    return false;
}
return permissions[access][permission];
}
Method Name: hasPermission

Example 7:
Method Body: {
return _entityCacheEnabled;
}
Method Name: isEntityCacheEnabled

Example 8:
Method Body: {
builder.setFlowClassNames(allocatorFlowNames).construct();
strategy = new LocalStorageAllocatorStrategy(builder);
return true;
}
Method Name: start

Example 9:
Method Body: {
for (VmNicInventory vmNic : nics) {
    VmNicType type = VmNicType.valueOf(vmNic.getType());
    VmInstanceNicFactory vnicFactory = vmMgr.getVmInstanceNicFactory(type);
    vnicFactory.releaseVmNic(vmNic);
}

SQL.New(VmNicVO.class).in(VmNicVO_.uuid, nics.stream().map(VmNicInventory::getUuid).collect(Collectors.toList())).delete();
}
Method Name: removeNicFromDb

Example 10:
Method Body: {
PreDeleteEventListener[] preListeners = getSession().getListeners().getPreDeleteEventListeners();
boolean veto = false;
if (preListeners.length>0) {
    PreDeleteEvent preEvent = new PreDeleteEvent( getInstance(), getId(), state, getPersister() ,(EventSource) getSession() );
    for ( int i = 0; i < preListeners.length; i++ ) {
        veto = preListeners[i].onPreDelete(preEvent) || veto;
    }
}
return veto;
}
Method Name: preDelete

Example 11:
Method Body: {
return credentials.username() + ":" + credentials.password();
}
Method Name: token

Example 12:
Method Body: {
Class type = getColumnType(field);
Index index = getIndex(field, type, true);
int t = ascend ? Index.TYPE_ASCENDING : Index.TYPE_DESCENDING;
return index.allRows(t);
}
Method Name: rowsSortedBy

Query:
Generate a Java method name for the following method body.
Use the similar examples as naming-style references.
Infer the most suitable naming pattern from the target method body and generate one concise, semantically accurate method name that reflects the method's functionality.
Return only the method name.
Do not output explanations or multiple candidates.

Method Body: __METHOD_BODY__
Method Name:"""

def parse_arguments():
    """Parse command line arguments"""
    arg_parser = argparse.ArgumentParser(description="Java method naming evaluation script")
    arg_parser.add_argument("--test_data_path", type=str, required=True,
                           help="Test data file path")
    arg_parser.add_argument("--output_file_path", type=str, required=True,
                           help="Output result file path")
    arg_parser.add_argument("--load_model_path", type=str, required=True,
                           help="Pretrained model path")
    arg_parser.add_argument("--batch_size", type=int, default=8,
                           help="Batch size")
    arg_parser.add_argument("--max_length", type=int, default=2048,
                           help="Maximum input sequence length")
    arg_parser.add_argument("--max_new_tokens", type=int, default=32,
                           help="Maximum number of new tokens to generate")
    return arg_parser.parse_args()

# Initialize Tree-sitter parser
def init_parser():
    try:
        from tree_sitter import Language, Parser
        JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
        parser = Parser()
        parser.set_language(JAVA_LANGUAGE)
        return parser
    except ImportError:
        logger.error("tree_sitter is not installed, please install tree_sitter first")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize tree_sitter: {e}")
        raise

class Example:
    def __init__(self, method_name, source_code):
        self.method_name = method_name
        self.source_code = source_code

def read_examples(filename):
    examples = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    examples.append(Example(
                        method_name=data.get('method_name', ''),
                        source_code=data.get('source_code', '')
                    ))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping line {line_num}, JSON parsing error: {e}")
                    continue
        logger.info(f"Successfully read {len(examples)} examples")
        return examples
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise

def find_first_method(node):
    if node.type == "method_declaration":
        return node
    for child in node.children:
        result = find_first_method(child)
        if result:
            return result
    return None

def mask_name(code: str, parser) -> str:
    try:
        code_bytes = code.encode('utf8')
        tree = parser.parse(code_bytes)
        root = tree.root_node
        method_node = find_first_method(root)
        if method_node:
            name_node = method_node.child_by_field_name("name")
            if name_node:
                start, end = name_node.start_byte, name_node.end_byte
                new_bytes = code_bytes[:start] + code_bytes[end:]
                return new_bytes.decode('utf8')
    except Exception as e:
        logger.warning(f"tree_sitter parsing failed: {e}")
    return code


def build_prompt(source_code: str) -> str:
    return PROMPT_TEMPLATE.replace(METHOD_BODY_PLACEHOLDER, source_code)


def approximate_token_spans(text):
    return list(re.finditer(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def truncate_source_code(source_code, max_length):
    template_without_body = PROMPT_TEMPLATE.replace(METHOD_BODY_PLACEHOLDER, "")
    prompt_budget = max_length - len(approximate_token_spans(template_without_body))

    if prompt_budget <= 0:
        return ""

    spans = approximate_token_spans(source_code)
    if len(spans) <= prompt_budget:
        return source_code

    cut_pos = spans[prompt_budget - 1].end()
    return source_code[:cut_pos]

def load_model_and_tokenizer(model_dir):
    """Load model and tokenizer"""
    logger.info(f"Loading model and tokenizer from {model_dir}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "left"
        
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        
        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer
    
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

def process_batch(batch, model, tokenizer, parser, args):
    """Process a batch of data"""
    descriptions = []
    method_names = []
    source_codes = []
    
    for ex in batch:
        try:
            code_no_name = mask_name(ex.source_code, parser)
            truncated_source = truncate_source_code(code_no_name, args.max_length)
            desc = build_prompt(truncated_source)
            descriptions.append(desc)
            method_names.append(ex.method_name)
            source_codes.append(ex.source_code)
        except Exception as e:
            logger.warning(f"Error processing example: {e}")
            truncated_source = truncate_source_code(ex.source_code, args.max_length)
            desc = build_prompt(truncated_source)
            descriptions.append(desc)
            method_names.append(ex.method_name)
            source_codes.append(ex.source_code)
    
    if not descriptions:
        return []
    
    inputs = tokenizer(
        descriptions,
        padding=True,
        truncation=True,
        max_length=args.max_length,
        return_tensors="pt"
    )
    
    device = next(model.parameters()).device
    inputs = inputs.to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False, 
            temperature=1.0
        )
    
    prompt_len = inputs['input_ids'].shape[1]
    results = []
    
    for out in outputs:
        gen_ids = out[prompt_len:]
        gen_text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        results.append(gen_text)
        

    batch_results = []
    for gold, pred, src in zip(method_names, results, source_codes):
        batch_results.append({
            "method_name": gold,
            "prediction": pred,
            "source_code": src
        })
    
    return batch_results

def main():
    """Main function"""
    args = parse_arguments()
    os.makedirs(os.path.dirname(args.output_file_path), exist_ok=True)
    parser = init_parser()
    

    model, tokenizer = load_model_and_tokenizer(args.load_model_path)

    examples = read_examples(args.test_data_path)
    
    if not examples:
        logger.error("No valid test data")
        return
    
    logger.info(f"Starting to process {len(examples)} examples with batch size: {args.batch_size}")
    
    with open(args.output_file_path, "w", encoding="utf-8") as fout:
        total_processed = 0
        
        for i in tqdm(range(0, len(examples), args.batch_size), desc="Processing batches"):
            batch = examples[i : i + args.batch_size]
            
            try:
                batch_results = process_batch(batch, model, tokenizer, parser, args)
                
                for result in batch_results:
                    fout.write(json.dumps(result, ensure_ascii=False) + "\n")
                    total_processed += 1
                    
            except Exception as e:
                logger.error(f"Error processing batch {i//args.batch_size + 1}: {e}")
                continue
    
    logger.info(f"Processing completed, total processed {total_processed} examples")
    logger.info(f"Results saved to: {args.output_file_path}")

if __name__ == "__main__":
    main()
