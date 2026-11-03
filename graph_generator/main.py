from supertype import Expression, Statement
from astparser import AstParser
from typing import Generator, List
from tree_sitter import Language, Parser, Node, Tree
from graph import Graph
from writefile import Writer
import argparse
from pathlib import Path
import logging


def traverseStatement(logger_error, methods, code, args, forder1, file):
    count = 0
    for item in methods:
        method, methodName = item
        graph = Graph()
        try:
            graph.build(method, code)
        except Exception as e:
            logger_error.error(f'{e.__class__.__name__}: {e}. Path: {forder1}/{file}/{methodName}')
            continue
        g = None
        if graph.getGraph(): 
            g = graph.getGraph()
        else:
            continue

        sourceCode = method.text.decode('utf-8')
        writer = Writer(project=forder1, file=file, methodName=methodName, code=sourceCode, ast=g['ast'], cfg=g['cfg'])
        # writer.writeFile('json', 'jsonfiles', f'{methodName}.json')
        format = args.format
        if 'ast' in args.type and 'cfg' in args.type:
            # if format == 'jsonl':
            if format == 'jsonl':
                writer.writeFile(format, Path(args.outputpath), 'data')
                count += 1
            # writer.writeFile(format, Path(args.outputpath) / f'{format}_files' / forder1, forder2)
            
            # elif format == 'dot' or format == 'json':
            #     writer.writeFile(format, Path(args.outputpath) / f'{format}_files' / forder)

            
        # writer.writeFile('dot', Path('pdffiles'), methodName)
        # writer.writeFile('jsonl', 'jsonlinefiles', 'data.jsonl')
        # cfg = g['cfg']
        # for node in cfg['nodes']:
        #     print(str(node.id) + ' : ' + node.label)
        # for edge in cfg['edges']:
        #     print(str(edge.source) + ' -> ' + str(edge.target))
        # print('--------------------------------------------')
    return count
        
            



            
def main():
    code = '''
    '''


    logger_info = logging.getLogger('info')
    logger_info.setLevel(logging.DEBUG)

    logger_error = logging.getLogger('error')
    logger_error.setLevel(logging.DEBUG)

    
    file_handler_info = logging.FileHandler("info.log", mode='w')
    file_handler_info.setLevel(logging.INFO)
    file_handler_info.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))

    file_handler_error = logging.FileHandler('error.log', mode='w')
    file_handler_error.setLevel(logging.ERROR)
    file_handler_error.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))

    logger_info.addHandler(file_handler_info)
    logger_error.addHandler(file_handler_error)



    


    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--inputpath", type=str, default='datasets/java-small/', help="source code file path")
    parser.add_argument("--outputpath", type=str, default='./processed_java-small_data/', help="output file path")
    parser.add_argument("--type", choices=['ast', 'cfg'], nargs="+", default=['ast', 'cfg'], type=str, help="type of graph to be generated")
    parser.add_argument("--format", choices=['json', 'dot', 'jsonl'], default='jsonl', type=str, help="format of output file")

    args = parser.parse_args()

    folder_path = Path(args.inputpath)

    folders1 = [f.name for f in folder_path.iterdir() if f.is_dir()]

    for folder1 in folders1:
        files = [f for f in (folder_path / folder1).rglob("*.java") if f.is_file()]
        count = 0
        methodCount = 0
        for count, file_path in enumerate(files, 1):
            with open(file_path, 'r', errors="ignore") as f:
                code = f.read()
            print(f'Processing {count}/{len(files)}: {file_path.relative_to(folder_path)}')
            astparser = AstParser()

            try:
                tree = astparser.parseAst(code)
            except Exception as e:
                logger_error.error(f'{e.__class__.__name__}: {e}. Path: {file_path.relative_to(folder_path)}')
                continue

            if code != '':
                methods = astparser.getMethods(code, tree)
                methodCount += traverseStatement(
                    logger_error, methods, code, args,
                    folder1, file_path.name
                )

        logger_info.info(f'Processed {methodCount} methods in {folder1}')

    # folders1 = [f.name for f in folder_path.iterdir() if f.is_dir()]
    # folders2 = []

    # for folder1 in folders1:
    #     folders2 = [f.name for f in Path(folder_path / folder1).iterdir() if f.is_dir()]
    #     for folder2 in folders2:
    #         files = [f for f in (folder_path / folder1 / folder2).rglob("*.java") if f.is_file()]
    #         count = 0
    #         methodCount = 0
    #         for count, file_path in enumerate(files, 1):
    #             with open(file_path, 'r', errors="ignore") as f:
    #                 code = f.read()
    #             print(f'Processing {count}/{len(files)}: {file_path.relative_to(folder_path)}')
    #             astparser = AstParser()

    #             try:
    #                 tree = astparser.parseAst(code)
    #             except Exception as e:
    #                 logger_error.error(f'{e.__class__.__name__}: {e}. Path: {file_path.relative_to(folder_path)}')
    #                 continue

    #             if code != '':
    #                 methods = astparser.getMethods(code, tree)
    #                 methodCount += traverseStatement(
    #                     logger_error, methods, code, args,
    #                     folder1, folder2, file_path.name
    #                 )

    #         logger_info.info(f'Processed {methodCount} methods in {folder1}/{folder2}')

            
    # astparser = AstParser()
    # try:
    #     tree = astparser.parseAst(code)
    # except Exception as e:
    #     print(f'{e.__class__.__name__}: {e}. Path: test/test.java')
    #     return
    # astparser = AstParser()
    # tree = astparser.parseAst(code)
    # methods = astparser.getMethods(code, tree)
    # traverseStatement(logger_error, methods, code, args, 'test', 'test.java')
    
    

if __name__ == "__main__":

    main()