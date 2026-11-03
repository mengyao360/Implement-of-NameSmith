from supertype import Expression, Statement
from nodeedge import Node, Edge
import networkx as nx
import numpy as np
import copy

class Graph:
    def __init__(self):
        self._ast = {
            'nodes': [],
            'edges': []
        }

        self._cfg = {
            'nodes': [],
            'edges': []
        }

    def build(self, method, code):
        sta = Statement(method, code, startmethod=True)
        nodes, ast, cfg = sta.handle()

        for key in ast:
            self._ast[key] = self._ast[key] + copy.deepcopy(ast[key])
        self.neworkxGraph(self._ast)
        self.reassign_ids('ast')
        for key in cfg:
            self._cfg[key] = self._cfg[key] + copy.deepcopy(cfg[key])

        self.neworkxGraph(self._cfg)
        self.reassign_ids('cfg')
        Node.setClassId(0)

    def reassign_ids(self, graph_type):
        if graph_type not in ['ast', 'cfg']:
            return
        
        graph = getattr(self, f'_{graph_type}')
        nodes = graph['nodes']
        edges = graph['edges']


        id_mapping = {}  
        for new_id, node in enumerate(nodes, start=0):
            id_mapping[node.id] = new_id
            node.id = new_id  


        for edge in edges:
            edge.source = id_mapping[edge.source]
            edge.target = id_mapping[edge.target]

    def neworkxGraph(self, graph):
        G = nx.DiGraph()
        nodes = graph['nodes']
        edges = graph['edges']
        
        for node in nodes:
            G.add_node(node.id, label=node.label)
        
        for edge in edges:
            G.add_edge(edge.source, edge.target)

        subgraph = None
        for i, component in enumerate(nx.weakly_connected_components(G)):
            
            subgraph = G.subgraph(component).copy()
            subnodes = list(subgraph.nodes)

            if 1 in subnodes:
                gedges = []
                gnodes = []
                for id, data in subgraph.nodes(data=True):
                    n = Node(data['label'])
                    n.setId(id)
                    gnodes.append(n)
                for u, v, data in subgraph.edges(data=True):
                    gedges.append(
                        Edge(u, v)
                    )
                graph['nodes'] = gnodes
                graph['edges'] = gedges
        return subgraph


    def getGraph(self):
        if self._ast['nodes'] == [] or self._cfg['nodes'] == []:
            return False
        return {
            'ast': self._ast,
            'cfg': self._cfg
        }

    # def buildMatrix(self, graph):
    #     G = nx.DiGraph()
    #     nodes = graph['nodes']
    #     edges = graph['edges']
        
    #     for node in nodes:
    #         G.add_node(node.id, label=node.label)
        
    #     for edge in edges:
    #         G.add_edge(edge.source, edge.target)

    #     for i, component in enumerate(nx.weakly_connected_components(G)):
    #         subgraph = G.subgraph(component).copy()
    #         nodes = list(subgraph.nodes)
    #         if 1 in nodes:
    #             adj_matrix = nx.adjacency_matrix(subgraph, nodelist=nodes).todense()

                

    #     return adj_matrix
    

# class Ast:
    
#     def __init__(self):
#         self._ast = {
#             'nodes': [],
#             'edges': []
#         }

#         # self.method_block = Node('method_block')
#         # self._ast['nodes'].append(self.method_block) 
    
#     def addNode(self, node):
#         self.cfgNode = node
    
#     def addEdge(self, edge):
#         self.cfgEdge = edge

#     def buildAst(self, block, code):
#         sta = Statement(block, code)
#         nodes, ast, cfg = sta.handle()
#         # if ast['nodes'] != []:
#         #     self._ast['edges'].append(Edge(self.method_block.id, ast['nodes'][0].id))
#         for key in ast:
#             self._ast[key] = self._ast[key] + ast[key]
#         return self._ast


# class Cfg:
    
#     def __init__(self):
#         self._cfg = {
#             'nodes': [],
#             'edges': []
#         }
    
#     def addNode(self, node):
#         self.cfgNode = node
    
#     def addEdge(self, edge):
#         self.cfgEdge = edge
        
#     def buildCfg(self, block, code):
#         sta = Statement(block, code)
#         nodes, ast, cfg = sta.handle()
#         for key in cfg:
#             self._cfg[key] = self._cfg[key] + cfg[key]
#         return self._cfg

        