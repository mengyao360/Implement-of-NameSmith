class Node:
    id = 1
    def __init__(self, label, type=''):
        self.id = Node.id
        Node.id += 1
        self.label = label
        self.type = type
        # self.defs = []
        # self.uses = []

    @classmethod
    def setClassId(cls, new_id):
        cls.id = new_id

    def setId(self, id):
        self.id = id
    

class Edge:
    def __init__(self,  source, target, type=''):
        self.source = source
        self.target = target
        self.edgeType = type
