import jsonlines
import json
import os
from pathlib import Path

from graphviz import Digraph

class Writer:

    def __init__(self, project, file, methodName, code, 
            ast, 
            cfg, 
            # pdg
        ):
        self._nodes=[]
        self._ast = ast
        self._cfg = cfg
        # self._pdg = pdg
        self._project = project
        self._file = file
        self._methodName = methodName
        self._code = code

    


    def constructNode(self, nodes):
        n = []
        if nodes != []:
            for node in nodes:
                n.append(
                    {
                        'id' : node.id,
                        'label' : node.label
                    }
                )
        return n

    def constructEdge(self, edges):
        e = []
        if edges != []:
            for edge in edges:
                e.append(
                    {
                        'source': edge.source,
                        'target': edge.target
                    }
                )
        return e
        

    def getNodes(self):
        return self._nodes

    def convertToJsonl(self, path):

        with jsonlines.open(path, mode='a') as writer:
            data = {
                'project': self._project,
                'file': self._file,
                'method_name': self._methodName,
                'source_code': self._code,
	            # 'comment': comment,
	            'ast': {
                    'nodes': self.constructNode(self._ast['nodes']),
                    'edges': self.constructEdge(self._ast['edges']),
                },
	            'cfg': {
                    'nodes': self.constructNode(self._cfg['nodes']),
                    'edges': self.constructEdge(self._cfg['edges']),
                }
                # 'pdg': {}
            }
            writer.write(data)

    def convertToJson(self, path, 
                    #   comment
                      ):
        with open(path, mode='w') as f:

            data = {
                'project': self._project,
                'file': self._file,
                'method_name': self._methodName,
                'sourcecode': self._code,
	            # 'comment': comment,
	            'ast': {
                    'nodes': self.constructNode(self._ast['nodes']),
                    'edges': self.constructEdge(self._ast['edges']),
                },
	            'cfg': {
                    'nodes': self.constructNode(self._cfg['nodes']),
                    'edges': self.constructEdge(self._cfg['edges']),
                }
                # 'pdg': {}
            }
            json.dump(data, f, indent=4)
            # json.dump(data, f, indent=4)
            # print(data)

    def convertToDot(self, path):

        astdot = Digraph()
        for node in self._ast['nodes']:
            astdot.node(str(node.id), node.label)
        for edge in self._ast['edges']:
            astdot.edge(str(edge.source), str(edge.target))

        astdot.render(path.with_name(path.stem + "_Ast.dot"), format='pdf', view=False)

        cfgdot = Digraph()
        for node in self._cfg['nodes']:
            cfgdot.node(str(node.id), node.label)
        for edge in self._cfg['edges']:
            cfgdot.edge(str(edge.source), str(edge.target))

        cfgdot.render(path.with_name(path.stem + "_Cfg.dot"), format='pdf', view=False)
    
    def writeFile(self, type, path, folder):
        # filename = path.name
        if type == 'json':
            path.mkdir(parents=True, exist_ok=True)
            self.convertToJson(path / f'{folder}.json')
        elif type == 'jsonl':
            path.mkdir(parents=True, exist_ok=True)
            self.convertToJsonl(path / f'{folder}.jsonl')
        elif type == 'dot':
            path.mkdir(parents=True, exist_ok=True)
            new_filename = self._file.replace(".java", "")
            self.convertToDot(path / f'{folder}' / f'{new_filename}_{self._methodName}')

        
            

    

