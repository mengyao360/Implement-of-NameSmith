from tree_sitter import Language, Parser, Node, Tree
from typing import Generator, List
import warnings


class AstParser:

    def __init__(self):
        warnings.simplefilter('ignore', FutureWarning) 

        Language.build_library(
        'treesitter_envs/build/java-languages.so',

        [
            'treesitter_envs/vendor/tree-sitter-java'
        ]
        )

        self.JAVA_LANGUAGE = Language('treesitter_envs/build/java-languages.so', 'java')
    
    
    def parseAst(self, code):
        self.parser = Parser()
        self.parser.set_language(self.JAVA_LANGUAGE)
        tree = self.parser.parse(bytes(code, "utf8"))

        # root_node = tree.root_node
        # print(root_node.sexp())
        
        # self.find_errors(tree.root_node)
        if tree.root_node.has_error:
            raise Exception(f"Syntax Error in Source Code")
        

        return tree
    
    def getMethods(self, code, tree: Tree) :
        cursor = tree.walk()
        visited_children = False
        while True:
            if not visited_children:
                if cursor.node and cursor.node.type == 'block' and cursor.node.parent.type == 'method_declaration':
                    method = cursor.node.parent.child_by_field_name('name')
                    # methodName = code[method.start_byte:method.end_byte]
                    methodName = method.text.decode('utf-8')
                    yield (cursor.node.parent, methodName)   
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break
