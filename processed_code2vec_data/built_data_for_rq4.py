import json
import random
import string
from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language('treesitter_envs/build/java-languages.so', 'java')

class JavaASTExtractor:
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

    def parse_code(self, code):
        return self.parser.parse(bytes(code, "utf8"))

    def construct_dict(self, node, dict):
        if node.type == "return_statement" or node.type == "yield_statement" or node.type == "enhanced_for_statement":
            for child in node.children:
                if child.type == "identifier":
                    name = child.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        if node.type == "formal_parameters" or node.type == "variable_declarator":
            for descendant in self.get_all_descendants(node):
                if descendant.type == "identifier":
                    name = descendant.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        if node.type == "assignment_expression":
            left = node.child_by_field_name('left')
            for descendant in ([left] if left.type == "identifier" else self.get_all_descendants(left)):
                if descendant.type == "identifier":
                    name = descendant.text.decode("utf-8")
                    dict.setdefault(name, random_string(len(name)))
        for child in node.children:
            self.construct_dict(child, dict)

    def get_all_descendants(self, node, lst=None):
        if lst is None:
            lst = []
        for c in node.children:
            lst.append(c)
            self.get_all_descendants(c, lst)
        return lst

def replace_identifiers(root, code, name_map):
    edits = []
    def visit(n):
        if n.type == "identifier":
            nm = n.text.decode("utf-8")
            if nm in name_map:
                edits.append((n.start_byte, n.end_byte, name_map[nm]))
        for c in n.children:
            visit(c)
    visit(root)
    for s, e, txt in sorted(edits, key=lambda x: -x[0]):
        code = code[:s] + txt + code[e:]
    return code

def random_string(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)

def main():
    inp = 'processed_code2vec_data/val.jsonl'
    out = 'processed_code2vec_data/val_transformed_rq4.jsonl'
    name_map_file = 'processed_code2vec_data/val_dict_rq4.jsonl' 

    extractor = JavaASTExtractor()

    with open(out, 'w', encoding='utf-8') as fo, \
         open(name_map_file, 'w', encoding='utf-8') as name_map_fo:  
        
        for idx, rec in enumerate(read_jsonl(inp)):
            project     = rec.get('project')
            file_path   = rec.get('file')
            method_name = rec.get('method_name')
            cfg         = rec.get('cfg', {})
            orig_ast    = rec.get('ast', {})
            src         = rec.get('source_code', '')

            tree = extractor.parse_code(src)
            name_map = {}
            extractor.construct_dict(tree.root_node, name_map)
            new_src = replace_identifiers(tree.root_node, src, name_map)

            name_map_record = {
                'index': idx,
                'project': project,
                'file': file_path,
                'method_name': method_name,
                'name_map': name_map
            }
            name_map_fo.write(json.dumps(name_map_record, ensure_ascii=False) + '\n')

            new_nodes = []
            for node in orig_ast.get('nodes', []):
                node_id = node.get('id')  
                label = node.get('label', '')
                lt = extractor.parse_code(label)
                new_label = replace_identifiers(lt.root_node, label, name_map)
                
                new_node = {
                    'id': node_id,  
                    'label': new_label
                }

                for key, value in node.items():
                    if key not in ['id', 'label']:
                        new_node[key] = value
                        
                new_nodes.append(new_node)

            new_rec = {
                'project':     project,
                'file':        file_path,
                'method_name': method_name,
                'source_code': new_src,
                'ast': {
                    'nodes': new_nodes,
                    'edges': orig_ast.get('edges', [])
                },
                'cfg': {
                    'nodes': cfg.get('nodes', []),
                    'edges': cfg.get('edges', [])
                }
            }
            # if idx < 10:
            #     print(new_src)
            #     print(new_nodes)

            fo.write(json.dumps(new_rec, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()