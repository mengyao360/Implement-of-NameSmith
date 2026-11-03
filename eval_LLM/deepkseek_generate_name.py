import argparse
import json
import logging
import os
import re
import time
from tree_sitter import Language, Parser, Node, Tree

from openai import OpenAI


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("DeepSeekEval")


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
        project_root = "/Users/mengyao/Documents/paper/NameSmith"
        build_dir = os.path.join(project_root, "build")
        library_path = os.path.join(build_dir, "java-languages.so")
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
    parser = argparse.ArgumentParser(description="Use DeepSeek API to predict Java method names.")
    parser.add_argument("--test_data_path", type=str, required=True, help="Input JSONL file path")
    parser.add_argument("--output_file_path", type=str, required=True, help="Output JSONL file path")
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-chat",
        help="DeepSeek model name, for example: deepseek-chat",
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="DeepSeek API key. If omitted, use DEEPSEEK_API_KEY from environment.",
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default="https://api.deepseek.com",
        help="DeepSeek API base URL",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,
        help="Maximum retries for each request",
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
        default=32,
        help="Maximum number of generated tokens",
    )
    parser.add_argument(
        "--request_interval",
        type=float,
        default=0.0,
        help="Seconds to sleep after each request to avoid rate limits",
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
                "Return only the method name."
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


def create_client(api_key, base_url):
    resolved_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not resolved_key:
        raise ValueError("Missing API key. Set DEEPSEEK_API_KEY or pass --api_key.")
    return OpenAI(api_key=resolved_key, base_url=base_url)


def predict_method_name(client, model, source_code, max_retries, max_length, max_new_tokens, parser):
    last_error = None
    masked_source_code = mask_name(source_code, parser)
    truncated_source_code = truncate_source_code(masked_source_code, max_length)
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=build_messages(truncated_source_code),
                max_tokens=max_new_tokens,
                stream=False,
            )
            content = response.choices[0].message.content
            return (content or "").strip()
        except Exception as exc:
            last_error = exc
            logger.warning("Request failed on attempt %s/%s: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                time.sleep(min(attempt, 5))
    raise RuntimeError(f"DeepSeek request failed after {max_retries} attempts: {last_error}")


def main():
    args = parse_arguments()

    output_dir = os.path.dirname(args.output_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    client = create_client(args.api_key, args.base_url)
    parser = init_parser()
    examples = read_examples(args.test_data_path)

    if not examples:
        logger.error("No valid examples found in %s", args.test_data_path)
        return

    total_processed = 0
    with open(args.output_file_path, "w", encoding="utf-8") as fout:
        for index, example in enumerate(examples, 1):
            try:
                prediction = predict_method_name(
                    client=client,
                    model=args.model,
                    source_code=example.source_code,
                    max_retries=args.max_retries,
                    max_length=args.max_length,
                    max_new_tokens=args.max_new_tokens,
                    parser=parser,
                )
                result = {
                    "method_name": example.method_name,
                    "prediction": prediction,
                    "source_code": example.source_code,
                }
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")
                total_processed += 1
                logger.info("Processed %s/%s", index, len(examples))
            except Exception as exc:
                logger.error("Failed to process example %s: %s", index, exc)

            if args.request_interval > 0:
                time.sleep(args.request_interval)

    logger.info("Finished. Processed %s examples.", total_processed)
    logger.info("Results saved to: %s", args.output_file_path)


if __name__ == "__main__":
    main()
