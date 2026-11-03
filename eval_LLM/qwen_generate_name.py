import argparse
import json
import logging
import os
import re
from tree_sitter import Language, Parser

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("QwenLocalEval")


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


class Example:
    def __init__(self, method_name, source_code):
        self.method_name = method_name
        self.source_code = source_code


def init_parser():
    try:
        project_root = "/model/bd-cx/my/baseline_LLM"
        build_dir = os.path.join(project_root, "build")
        library_path = os.path.join(build_dir, "my-languages.so")
        vendor_dir = os.path.join(project_root, "node4", "tree-sitter-java")

        if not os.path.exists(library_path):
            if not os.path.exists(vendor_dir):
                raise FileNotFoundError(
                    f"tree-sitter-java grammar repo not found: {vendor_dir}"
                )
            os.makedirs(build_dir, exist_ok=True)
            Language.build_library(
                library_path,
                [vendor_dir],
            )

        java_language = Language(library_path, "java")
        parser = Parser()
        parser.set_language(java_language)
        return parser
    except ImportError:
        logger.error("tree_sitter is not installed, please install tree_sitter first.")
        raise
    except Exception as exc:
        logger.error("Failed to initialize tree_sitter: %s", exc)
        raise


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Use a local Qwen model to predict Java method names."
    )
    parser.add_argument("--test_data_path", type=str, required=True, help="Input JSONL file path")
    parser.add_argument("--output_file_path", type=str, required=True, help="Output JSONL file path")
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen3.5-9B",
        help="Local Hugging Face model name or local model path",
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=2048,
        help="Approximate maximum input token length",
    )
    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=64,
        help="Maximum number of generated tokens",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. Set 0 for greedy decoding.",
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=0.9,
        help="Top-p sampling parameter used when temperature > 0.",
    )
    parser.add_argument(
        "--trust_remote_code",
        action="store_true",
        help="Whether to enable trust_remote_code when loading tokenizer/model.",
    )
    return parser.parse_args()


def read_examples(filename):
    examples = []
    with open(filename, "r", encoding="utf-8") as file_obj:
        for line_num, line in enumerate(file_obj, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                examples.append(
                    Example(
                        method_name=data.get("method_name", ""),
                        source_code=data.get("source_code", ""),
                    )
                )
            except json.JSONDecodeError as exc:
                logger.warning("Skip line %s because JSON parsing failed: %s", line_num, exc)
    logger.info("Loaded %s examples from %s", len(examples), filename)
    return examples


def find_first_method(node):
    if node.type == "method_declaration":
        return node
    for child in node.children:
        result = find_first_method(child)
        if result:
            return result
    return None


def mask_name(code, parser):
    try:
        code_bytes = code.encode("utf8")
        tree = parser.parse(code_bytes)
        root = tree.root_node
        method_node = find_first_method(root)
        if method_node:
            name_node = method_node.child_by_field_name("name")
            if name_node:
                start, end = name_node.start_byte, name_node.end_byte
                new_bytes = code_bytes[:start] + code_bytes[end:]
                return new_bytes.decode("utf8")
    except Exception as exc:
        logger.warning("tree_sitter parsing failed: %s", exc)
    return code


def build_messages(source_code):
    prompt = PROMPT_TEMPLATE.replace(METHOD_BODY_PLACEHOLDER, source_code)
    return [
        {
            "role": "system",
            "content": (
                "You generate concise and semantically accurate Java method names. "
                "Return only one Java method name. "
                "Do not output reasoning, thinking process, explanations, prefixes, or code fences."
            ),
        },
        {"role": "user", "content": prompt},
    ]


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


def resolve_dtype():
    if torch.cuda.is_available():
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return torch.float32


def load_model_and_tokenizer(model_name, trust_remote_code):
    dtype = resolve_dtype()
    logger.info("Loading tokenizer from %s", model_name)
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
    )

    logger.info("Loading model from %s", model_name)
    model_kwargs = {
        "dtype": dtype,
        "trust_remote_code": trust_remote_code,
    }

    if torch.cuda.is_available():
        model_kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

    if not torch.cuda.is_available():
        model = model.to("cpu")

    model.eval()
    return tokenizer, model


def extract_prediction_text(tokenizer, generated_ids, input_ids):
    output_ids = generated_ids[0][len(input_ids[0]) :]
    content = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    content = re.sub(r"^Thinking Process:\s*", "", content, flags=re.IGNORECASE).strip()

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    for line in reversed(lines):
        line = line.strip("`").strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line):
            return line

    match = re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\b", content)
    if match:
        return match.group(0)

    return content


def predict_method_name(
    tokenizer,
    model,
    source_code,
    max_length,
    max_new_tokens,
    temperature,
    top_p,
    parser,
):
    masked_source_code = mask_name(source_code, parser)
    truncated_source_code = truncate_source_code(masked_source_code, max_length)
    messages = build_messages(truncated_source_code)

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        enable_thinking=False,
        add_generation_prompt=True,
    )

    model_inputs = tokenizer([text], return_tensors="pt")
    model_inputs = {k: v.to(model.device) for k, v in model_inputs.items()}

    generate_kwargs = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
    }

    if temperature and temperature > 0:
        generate_kwargs["do_sample"] = True
        generate_kwargs["temperature"] = temperature
        generate_kwargs["top_p"] = top_p
    else:
        generate_kwargs["do_sample"] = False

    with torch.no_grad():
        generated_ids = model.generate(**model_inputs, **generate_kwargs)

    return extract_prediction_text(
        tokenizer=tokenizer,
        generated_ids=generated_ids,
        input_ids=model_inputs["input_ids"],
    )


def main():
    args = parse_arguments()

    output_dir = os.path.dirname(args.output_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    parser = init_parser()
    examples = read_examples(args.test_data_path)

    if not examples:
        logger.error("No valid examples found in %s", args.test_data_path)
        return

    tokenizer, model = load_model_and_tokenizer(
        model_name=args.model,
        trust_remote_code=args.trust_remote_code,
    )

    total_processed = 0
    with open(args.output_file_path, "w", encoding="utf-8") as fout:
        for index, example in enumerate(examples, 1):
            try:
                prediction = predict_method_name(
                    tokenizer=tokenizer,
                    model=model,
                    source_code=example.source_code,
                    max_length=args.max_length,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    parser=parser,
                )
                result = {
                    "method_name": example.method_name,
                    "prediction": prediction,
                    "source_code": example.source_code,
                }
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")
                fout.flush()
                total_processed += 1
                logger.info("Processed %s/%s", index, len(examples))
            except Exception as exc:
                logger.error("Failed to process example %s: %s", index, exc)

    logger.info("Finished. Processed %s examples.", total_processed)
    logger.info("Results saved to: %s", args.output_file_path)


if __name__ == "__main__":
    main()
