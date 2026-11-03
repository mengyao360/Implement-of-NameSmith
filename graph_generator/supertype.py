'''
  supertypes: $ => [
    $.expression,
    $.declaration,
    $.statement,
    $.primary_expression,
    $._literal,
    $._type,
    $._simple_type,
    $._unannotated_type,
    $.comment,
    $.module_directive,
  ]
'''
from nodeedge import Node, Edge
import re
import numpy as np
import networkx as nx

class Expression:
    '''
    expression: $ => choice(
      $.assignment_expression,
      $.binary_expression,
      $.instanceof_expression,
      $.lambda_expression,
      $.ternary_expression,
      $.update_expression,
      $.primary_expression,
      $.unary_expression,
      $.cast_expression,
      $.switch_expression,
    )
    '''

    def __init__(self, astNode, code):
        self._expressions = [
            'assignment_expression',
            'binary_expression',
            'instanceof_expression',
            'lambda_expression',
            'ternary_expression',
            'update_expression',
            'primary_expression',
            'unary_expression',
            'cast_expression',
            'switch_expression'
        ]
        # AST node
        self._astNode = astNode
        # Node
        self._node = []
        # source code
        self._code = code

    def isExoressionNode(self):
        if self._astNode.type in self._expressions:
            print('isExoressionNode(self)')
            return True
        else:
            return False
    def getNodes(self):
        return self._node

    def handle(self):
        if self._astNode.type == 'assignment_expression':
            self.handleAssignment()
            return self.getNodes()
        elif self._astNode.type == 'binary_expression':
            self.handleBinary()
            return self.getNodes()
        elif self._astNode.type == 'instanceof_expression':
            self.handleInstanceof()
            return self.getNodes()
        elif self._astNode.type == 'lambda_expression':
            self.handleLambda()
            return self.getNodes()
        elif self._astNode.type == 'ternary_expression':
            self.handleTernary()
            return self.getNodes()
        elif self._astNode.type == 'update_expression':
            self.handleUpdate()
            return self.getNodes()
        elif self._astNode.type == 'primary_expression':
            self.handlePrimary()
            return self.getNodes()
        elif self._astNode.type == 'unary_expression':
            self.handleUnary()
            return self.getNodes()
        elif self._astNode.type == 'cast_expression':
            self.handleCast()
            return self.getNodes()
        elif self._astNode.type == 'switch_expression':
            self.handleSwitch()
            return self.getNodes()

        else:
            print('error: not expression type. node type: {}'.format(self.astNode.type))
    
    def handleAssignment(self):
        # defs = []
        # uses = []
        # left = self._node.child_by_field_name('left')
        # defs.append(left)
        # right = self._node.child_by_field_name('right')
        # uses.append(right)  

        # label = self._code[self._node.start_byte:self._node.end_byte]
        label = self._node.text.decode('utf-8')

        self._node.append(Node(label))

    def handleBinary():
        pass
    def handleInstanceof():
        pass
    def handleLambda():
        pass
    def handleTernary():
        pass
    def handleUpdate():
        pass
    def handlePrimary():
        pass
    def handleUnary():
        pass
    def handleCast():
        pass
    def handleSwitch():
        pass

class Declaration:
    '''

    '''
    def __init__(self, astNode, code):
        self.statements = [
            

        ]
        # AST node
        self._astNode = astNode
        # Node
        self._node = []
        # source code
        self._code = code

class Statement:
    '''
        statement: $ => choice(
      $.declaration,
      $.expression_statement,
      $.labeled_statement,
      $.if_statement,
      $.while_statement,
      $.for_statement,
      $.enhanced_for_statement,
      $.block,
      ';',
      $.assert_statement,
      $.do_statement,
      $.break_statement,
      $.continue_statement,
      $.return_statement,
      $.yield_statement,
      $.switch_expression, // switch statements and expressions are identical
      $.synchronized_statement,
      $.local_variable_declaration,
      $.throw_statement,
      $.try_statement,
      $.try_with_resources_statement
    ),
    '''
    
    
    def __init__(self, astNode, code, level=0, iflevel=0, continuelevel=0, trylevel=0, yieldLevel=0, startmethod = False,):
        
        self._declarations = [
            'module_declaration',
            'package_declaration',
            'import_declaration',
            'class_declaration',
            'record_declaration',
            'interface_declaration',
            'annotation_type_declaration',
            'enum_declaration',
        ]

        self._statements = [
            # first statement to process
            'method_declaration',

            'declaration',
            self._declarations,

            'expression_statement',
            'labeled_statement',
            'if_statement',
            'while_statement',
            'for_statement',
            'enhanced_for_statement',
            'block',
            'assert_statement',
            'do_statement',
            'break_statement',
            'continue_statement',
            'return_statement',
            'yield_statement',
            'switch_expression',
            'synchronized_statement',
            'local_variable_declaration',
            'throw_statement',
            'try_statement',
            'try_with_resources_statement',
            'class_declaration',
            'class_body'
        ]

        

        self._class_body_declaration = [
            'field_declaration',
            'record_declaration',
            'method_declaration',
            'compact_constructor_declaration',
            'class_declaration',
            'interface_declaration',
            'annotation_type_declaration',
            'enum_declaration',
            'block',
            'static_initializer',
            'constructor_declaration',
        ]

        self._ignoreStatement = [
            '{',
            '}',
            'line_comment',
            'block_comment',
            ':',
            ';'
        ]

        self._startMethod = startmethod
        # AST node
        self._astNode = astNode
        # node for construct cfg
        self._node = []
        # the ast that construct for current node
        self._ast = {
            'nodes': [],
            'edges': []
        }
        # the cfg that construct for current statement
        self._subcfg = {
            'nodes': [],
            'edges': []
        }
        # the cfg that construct for current node
        self._cfg = {
            'nodes': [],
            'edges': []
        }

        self._stopStatement = ['break_statement', 'continue_statement', 'return_statement', 'throw_statement', 'yield_statement', 'identifier_break_statement', 'identifier_continue_statement'] 
        # source code
        self._code = code
        # last Node of this statement
        self._lastNode = []

        # continue level
        self._continueLevel = continuelevel
        self._continueLevelStatement = ['for_statement', 'while_statement', 'enhanced_for_statement', 'do_statement']
        self._continueLevelNode = []

        # level is breakLevel
        self._level = level
        self._levelStatement = ['for_statement', 'while_statement', 'enhanced_for_statement', 'switch_expression', 'do_statement']
        self._levelNode = []

        self._tryLevel = trylevel
        self._throwNode = []

        self._ifLevel = iflevel
        self._ifLevelNode = []
        self._lastIfNode = None

        self._yieldLevel = yieldLevel
        self._yieldNode = []

        self._identifierBreakNode = None

        self._switchLastNode = []
    def isStatementNode(self):
        if self._astNode.type in self._statements:
            return True
        else:
            return False
        
    def getNodes(self):
        return self._node
    
    def getAst(self):
        return self._ast
    
    def getCfg(self):
        return self._cfg
    
    def astBulider(self, sourceNode, targetNode=None):
        if targetNode is not None:
            if sourceNode not in self._ast['nodes']:
                self._ast['nodes'].append(sourceNode)
            if targetNode not in self._ast['nodes']:
                self._ast['nodes'].append(targetNode)
            self._ast['edges'].append(Edge(sourceNode.id, targetNode.id))
        else:
            if sourceNode not in self._ast['nodes']:
                self._ast['nodes'].append(sourceNode)

    def cfgEdgeAdd(self, edge):
        mark = 0
        for e in self._cfg['edges']:
            if edge.source == e.source and edge.target == e.target:
                mark = 1
        if mark == 0:
            self._cfg['edges'].append(edge)

    def cfgBulider(self, sourceNode, targetNode=None):
        if targetNode is not None:
            if sourceNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(sourceNode)
            if targetNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(targetNode)
            edge = Edge(sourceNode.id, targetNode.id)
            self.cfgEdgeAdd(edge)
            # self._cfg['edges'].append(Edge(sourceNode.id, targetNode.id))
            # if sourceNode.id == 24 and targetNode.id == 7:
            #     print('hhh')
        else:
            if sourceNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(sourceNode)

    def cfgBuiderForElseEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)
    
    def cfgBuiderForReturnEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)

    def existReturnEdge(self, sourceNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return True
        return False

    def cfgBuiderForBreakEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)

    def cfgBuiderForContinueEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)

    def cfgBuiderForThrowEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)

    def cfgBuiderForYieldEdge(self, sourceNode, targetNode):
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                return
        self.cfgBulider(sourceNode, targetNode)

    def cfgBuiderForIfEdge(self, sourceNode, targetNode):
        count = 0
        for e in self._cfg['edges']:
            if sourceNode.id == e.source:
                count += 1
        if count >= 2:
            return
        self.cfgBulider(sourceNode, targetNode)
    
# add nodes and edges for ast
    def astJoint(self, ast):
        for key in self._ast:
            seen = set()
            v = []
            for item in self._ast[key] + ast[key]:

                if item not in seen:
                    seen.add(item)
                    self._ast[key].clear()
                    v.append(item)
            self._ast[key] = v

# add nodes and edges for cfg
    def cfgJoint(self, cfg):
        for key in self._cfg:
            seen = set()
            v = []
            for item in self._cfg[key] + cfg[key]:
                if item not in seen:
                    seen.add(item)
                    self._cfg[key].clear()
                    v.append(item)
            self._cfg[key] = v
    # break level
    def levelNodeAdd(self, node):
        
        for level, item in self._levelNode:
            if node[1] == item:
                return
        self._levelNode.append(node)
    
    def levelNodeListAdd(self, nodes):
        seen = set()
        v = []
        for level, item in self._levelNode + nodes:
            if item not in seen:
                seen.add(item)
                self._levelNode.clear()
                v.append((level, item))
        self._levelNode = v

    def breakChildAdd(self, breaklist, i, node):
        for index, level, item in breaklist:
            if node[1] == item:
                return
        breaklist.append((i, node[0], node[1]))

    def breakChildCfgBuider(self, sourceNode, targetNode=None):
        if targetNode is not None:
            if sourceNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(sourceNode)
            if targetNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(targetNode)
            edge = Edge(sourceNode.id, targetNode.id)
            self.cfgEdgeAdd(edge)
        else:
            if sourceNode not in self._cfg['nodes']:
                self._cfg['nodes'].append(sourceNode)
    def chageNodeLevel(self, node):
        for i, (level, item) in enumerate(self._levelNode):
            if node==item:
                new = (level+1, item)
                self._levelNode.pop(i)
                self._levelNode.insert(i, new)

    def continueLevelNodeAdd(self, node):
        
        for level, item in self._continueLevelNode:
            if node[1] == item:
                return
        self._continueLevelNode.append(node)
    
    def continueLevelNodeListAdd(self, nodes):
        seen = set()
        v = []
        for level, item in self._continueLevelNode + nodes:
            if item not in seen:
                seen.add(item)
                self._continueLevelNode.clear()
                v.append((level, item))
        self._continueLevelNode = v

    def throwLevelNodeAdd(self, node):
        
        for level, item in self._throwNode:
            if node[1] == item:
                return
        self._throwNode.append(node)
    
    def throwLevelNodeListAdd(self, nodes):
        seen = set()
        v = []
        for level, item in self._throwNode + nodes:
            if item not in seen:
                seen.add(item)
                self._throwNode.clear()
                v.append((level, item))
        self._throwNode = v
    
    def yieldLevelNodeAdd(self, node):
        
        for level, item in self._yieldNode:
            if node[1] == item:
                return
        self._yieldNode.append(node)
    
    def yieldLevelNodeListAdd(self, nodes):
        seen = set()
        v = []
        for level, item in self._yieldNode + nodes:
            if item not in seen:
                seen.add(item)
                self._yieldNode.clear()
                v.append((level, item))
        self._yieldNode = v

    def ifLevelNodeAdd(self, node):
        
        for level, ifLevel, item in self._ifLevelNode:
            if node[2] == item:
                return
        self._ifLevelNode.append(node)
    
    def ifLevelNodeListAdd(self, nodes):
        seen = set()
        v = []
        for level, ifLevel, item in self._ifLevelNode + nodes:
            if item not in seen:
                seen.add(item)
                self._ifLevelNode.clear()
                v.append((level, ifLevel, item))
        self._ifLevelNode = v


    def ifOrElseChildAdd(self, ifOrElseChild, i, node):
        for j, level , ifLevel, n in ifOrElseChild:
            if node[2] == n:
                return
        ifOrElseChild.append((i, node[0], node[1], node[2]))

    def lastNodeListAdd(self, nodes):
        for n in nodes:
            self._lastNode.append(n)
    
    # def delNode(self, node):
    #     for i, n in enumerate(self._node):
    #         if node == n:
    #             self._node.pop(i)
        
    #     for i, n in enumerate(self._ast['nodes']):
    #         if node == n:
    #             self._ast['nodes'].pop(i)

    #     for i, n in enumerate(self._cfg['edges']):
    #         if node.id == n.source:
    #             self._cfg['edges'].pop(i)
        
    #     for i, n in enumerate(self._cfg['nodes']):
    #         if node == n:
    #             self._cfg['nodes'].pop(i)
        
    #     for i, n in enumerate(self._cfg['edges']):
    #         if node.id == n.source:
    #             self._cfg['edges'].pop(i)


    def handle(self):
        if self._astNode.type in self._ignoreStatement:
            return (self.getNodes(), self.getAst(), self.getCfg())
        if self.isStatementNode():
            if self._astNode.type in self._declarations:
                self.handleDeclaration()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'class_body':
                self.handleClassBody()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'method_declaration':
                self.handleMethodDeclaration()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'expression_statement':
                self.handleExpression()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'labeled_statement':
                self.handleLabeled()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'if_statement':
                self.handleIf()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'while_statement':
                self.handleWhile()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'for_statement':
                self.handleFor()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'enhanced_for_statement':
                self.handleEnhanced()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'block':
                self.handleBlock()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'assert_statement':
                self.handleAssert()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'do_statement':
                self.handleDo()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'break_statement':
                self.handleBreak()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'continue_statement':
                self.handleContinue()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'return_statement':
                self.handleReturn()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'yield_statement':
                self.handleYield()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'switch_expression':
                self.handleSwitch()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'synchronized_statement':
                self.handleSynchronized()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'local_variable_declaration':
                self.handleLocalVariable()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'throw_statement':
                self.handleThrow()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'try_statement':
                self.handleTry()
                return (self.getNodes(), self.getAst(), self.getCfg())
            elif self._astNode.type == 'try_with_resources_statement':
                self.handleTryWithResources()
                return (self.getNodes(), self.getAst(), self.getCfg())
            # elif self._astNode.type == 'class_declaration':
            #     self.handleClassDeclaration()
            #     return (self.getNodes(), self.getAst(), self.getCfg())
            
            # elif self._astNode.type in self._class_body_declaration:
            #     self.handleClassBody()
            #     return (self.getNodes(), self.getAst(), self.getCfg())
            # elif str(self._astNode.type) == '{' or str(self._astNode.type) == '}':
            #     pass
        else:
            print('error: not statement type. node type: {}, code: {}, parent: {}'.format(self._astNode.type, self._code[self._astNode.start_byte:self._astNode.end_byte], self._astNode.parent))
    
    def handleDeclaration(self):
        '''
        declaration: $ => prec(PREC.DECL, choice(
            $.module_declaration,
            $.package_declaration,
            $.import_declaration,
            $.class_declaration,
            $.record_declaration,
            $.interface_declaration,
            $.annotation_type_declaration,
            $.enum_declaration,
        )),
        '''
        raise NotImplementedError('handleDeclaration()')
        if self._astNode.type == 'module_declaration':
            self.handleModuleDeclaration()

        elif self._astNode.type == 'package_declaration':
            self.handlePackageDeclaration()

        elif self._astNode.type == 'import_declaration':
            self.handleImportDeclaration()

        elif self._astNode.type == 'class_declaration':
            self.handleClassDeclaration()

        elif self._astNode.type == 'record_declaration':
            self.handleRecordDeclaration()

        elif self._astNode.type == 'interface_declaration':
            self.handleInterfaceDeclaration()

        elif self._astNode.type == 'annotation_type_declaration':
            self.handleAnnotationTypeDeclaration()

        elif self._astNode.type == 'enum_declaration':
            self.handleEnumDeclaration()

    
    def handleModuleDeclaration(self):
        '''
        module_declaration: $ => seq(
            repeat($._annotation),
            optional('open'),
            'module',
            field('name', $._name),
            field('body', $.module_body),
        ),
        '''
        parent = Node('module')
        label = ''
        classBodyNode = self._astNode.child_by_field_name('body')

        node1 = Node(self._astNode.type) 

        
        # node5 = Node('annotation')
        # self.astBulider(parent, node5)

        
        # childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        # for i, child in enumerate(childList):
        #     if child.type == 'open' or child.type == 'module':
        #         label = label + self._code[child.start_byte:child.end_byte] + ' '
        # nameNode = self._astNode.child_by_field_name('name')
        # label = label + self._code[nameNode.start_byte:nameNode.end_byte]
        # node2 = Node(label)

        # cfgs = []
        # for i, child in enumerate(childList):
        #     if child.type == 'open' or child.type == 'module':
        #         break
        #     node3 = Node(child.type)
        #     node4 = Node(self._code[child.start_byte:child.end_byte])
        #     cfgs.append(node4)
        #     self.astBulider(node5, node3)
        #     self.astBulider(node3, node4)
        # self.astBulider(parent, node1)
        # self.astBulider(node1, node2)

        # if cfgs != []:
        #     for i in range(len(cfgs)):
        #         if i+1 < len(cfgs):
        #             self.cfgBulider(cfgs[i], cfgs[i+1])
        # self.cfgBulider(cfgs[-1], node2)



        label = self._code[self._astNode.start_byte:classBodyNode.start_byte]
        node2 = Node(label)

        self.cfgBulider(node2)

        self.astBulider(parent, node1)
        self.astBulider(node1, node2)   

        bodySta = None
        bodySta = Statement(classBodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handleMoudleBody()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        # self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
        # return (self.getNodes(), self.getAst(), self.getCfg())

    def handleMoudleBody(self):
        '''
        module_body: $ => seq(
            '{',
            repeat($.module_directive),
            '}',
        ),

        module_directive: $ => choice(
            $.requires_module_directive,
            $.exports_module_directive,
            $.opens_module_directive,
            $.uses_module_directive,
            $.provides_module_directive,
        ),
        '''
        parent = Node('module_body')
        cfgs = []
        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        for i, child in enumerate(childList):
            if child.type == 'requires_module_directive':
                node1 = Node(child.type)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                cfgs.append(node2)
                self.astBulider(parent, node1)
                self.astBulider(node1, node2)
            elif child.type == 'exports_module_directive':
                node1 = Node(child.type)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                cfgs.append(node2)
                self.astBulider(parent, node1)
                self.astBulider(node1, node2)
            elif child.type == 'opens_module_directive':
                node1 = Node(child.type)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                cfgs.append(node2)
                self.astBulider(parent, node1)
                self.astBulider(node1, node2)
            elif child.type == 'uses_module_directive':
                node1 = Node(child.type)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                cfgs.append(node2)
                self.astBulider(parent, node1)
                self.astBulider(node1, node2)
            elif child.type == 'provides_module_directive':
                node1 = Node(child.type)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                cfgs.append(node2)
                self.astBulider(parent, node1)
                self.astBulider(node1, node2)
            else:
                print('wrong')
        if cfgs != []:
            for i in range(len(cfgs)):
                if i+1 < len(cfgs):
                    self.cfgBulider(cfgs[i], cfgs[i+1])
                    
        if cfgs != []:
            self._lastNode.append(cfgs[-1])
        # self._lastNode.append(cfgs[-1])

        return (self.getNodes(), self.getAst(), self.getCfg())
    def handlePackageDeclaration(self):
        '''
        package_declaration: $ => seq(
            repeat($._annotation),
            'package',
            $._name,
            ';',
        ),
        '''
        # parent = Node('Package')
        # label = ''

        # node1 = Node(self._astNode.type) 
        # node5 = Node('annotation')
        # self.astBulider(parent, node5)

        # startByte = None
        # childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        
        # cfgs = []
        # for i, child in enumerate(childList):
        #     if child.type == 'package':
        #         # label = label + self._code[child.start_byte:child.end_byte] + ' '
        #         startByte = child.start_byte
        #         break
        #     node3 = Node(child.type)
        #     node4 = Node(self._code[child.start_byte:child.end_byte])
        #     cfgs.append(node4)
        #     self.astBulider(node5, node3)
        #     self.astBulider(node3, node4)
        # label = self._code[startByte:self._astNode.end_byte]
        # node2 = Node(label)
        # self.astBulider(parent, node1)
        # self.astBulider(node1, node2)
        # self._lastNode.append(node2)

        # if cfgs != []:
        #     for i in range(len(cfgs)):
        #         if i+1 < len(cfgs):
        #             self.cfgBulider(cfgs[i], cfgs[i+1])

        # self.cfgBulider(cfgs[-1], node2)

        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label)
        self._lastNode.append(node1)
        self._node.append(node1)
        self.yieldLevelNodeAdd((self._yieldLevel, node1))
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

        

    def handleImportDeclaration(self):
        '''
        import_declaration: $ => seq(
            'import',
            optional('static'),
            $._name,
            optional(seq('.', $.asterisk)),
            ';',
        ),
        '''

        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        lable = self._astNode.text.decode('utf-8')


        node1 = Node(label)
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    
    def handleExpression(self):
        
        '''
        expression_statement: $ => seq(
            $.expression,
            ';'
        ),

        expression: $ => choice(
            $.assignment_expression,
            $.binary_expression,
            $.instanceof_expression,
            $.lambda_expression,
            $.ternary_expression,
            $.update_expression,
            $.primary_expression,
            $.unary_expression,
            $.cast_expression,
            $.switch_expression,
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')
        node1 = Node(label)
        self._lastNode.append(node1)
        self._node.append(node1)

        self.astBulider(parent, node1)
        
        self.cfgBulider(node1)

    def handleLabeled(self):
        '''
        labeled_statement: $ => seq(
            $.identifier, ':', $.statement
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''

        
        statementNode = []
        node2 = None
        identifierAstChild = None
        for child in self._astNode.children:
            if child.type == 'identifier':
                identifierAstChild = child
                node1 = Node(child.type)
                self.astBulider(parent, node1)

                # label = self._code[child.start_byte:child.end_byte] + ': '
                label = child.text.decode('utf-8') + ': '
                node2 = Node(label)

                self.cfgBulider(node2)

                self._node.append(node2)

                self.astBulider(node1, node2)
                
            if child.type in self._statements:
                sta = None
                sta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = sta.handle()
                if cfg['nodes'] != []:
                    self.lastNodeListAdd(sta._lastNode)
                else:
                    self._lastNode.append(node2)
                # self.lastNodeListAdd(sta._lastNode)
                self.continueLevelNodeListAdd(sta._continueLevelNode)
                self.levelNodeListAdd(sta._levelNode)
                self.ifLevelNodeListAdd(sta._ifLevelNode)
                self.throwLevelNodeListAdd(sta._throwNode)
                self.yieldLevelNodeListAdd(sta._yieldNode)
                if ast['nodes'] != []:
                    node3 = ast['nodes'][0]
                    self.astBulider(parent, node3)
                    self.astJoint(ast)

                if cfg['nodes'] != []:
                    node4 = cfg['nodes'][0]
                    self.cfgBulider(node2, node4)
                    self.cfgJoint(cfg)
                    
                    for node in cfg['nodes']:
                        if node2.label in node.label:
                            self.cfgBulider(node, node2)

                        if node.type == 'identifier_break_statement' or node.type == 'identifier_continue_statement':
                            # if self._code[identifierAstChild.start_byte:identifierAstChild.end_byte] in node.label:
                            if identifierAstChild.text.decode('utf-8') in node.label:
                                self.cfgBulider(node, node2)


        if statementNode != []:
            self._node.extend(statementNode)
             
    def handleIf(self):
        '''
        if_statement: $ => prec.right(seq(
            'if',
            field('condition', $.condition),
            field('consequence', $.statement),
            optional(seq('else', field('alternative', $.statement)))
        )),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        ifLabel = 'if '
        elseLabel = 'else '

        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        label = label + ifLabel
        # conditionNode is AST node for condition field
        conditionNode = self._astNode.child_by_field_name('condition')
        # label = label + self._code[conditionNode.start_byte:conditionNode.end_byte]
        label = label + conditionNode.text.decode('utf-8') + ' '
        node1 = Node('condition')
        self.astBulider(parent, node1)

        node2 = Node(label, type='if_condition')

        self.cfgBulider(node2)

        self._node.append(node2)
        self.astBulider(node1, node2)

        
        # consequence field
        consequenceNode = self._astNode.child_by_field_name('consequence')
        consequenceSta = None
        consequenceSta = Statement(consequenceNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = consequenceSta.handle()
        # these need to write after handle method
        # if len(consequenceSta._lastNode) == 1:
        #     # for n in consequenceSta._lastNode:
        #     # if consequenceSta._lastNode[0].type != 'break_statement' and consequenceSta._lastNode[0].type != 'continue_statement' and consequenceSta._lastNode[0].type != 'throw_statement':
        #     if consequenceSta._lastNode[0].type not in self._stopStatement:
        #         self.lastNodeListAdd(consequenceSta._lastNode)
        # elif len(consequenceSta._lastNode) > 1:
        #     for n in consequenceSta._lastNode:
        #         # if n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
        #         if n.type not in self._stopStatement:
        #             self._lastNode.append(n)
        # else:
        #     self.lastNodeListAdd(consequenceSta._lastNode)
        self.lastNodeListAdd(consequenceSta._lastNode)
        self.levelNodeListAdd(consequenceSta._levelNode)
        self.continueLevelNodeListAdd(consequenceSta._continueLevelNode)
        self.ifLevelNodeListAdd(consequenceSta._ifLevelNode)
        self.throwLevelNodeListAdd(consequenceSta._throwNode)
        self.yieldLevelNodeListAdd(consequenceSta._yieldNode)
        # node3 = Node(consequenceNode.type)
        # self.astBulider(parent, node3)

        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node4 = ast['nodes'][0]
            self.astBulider(parent, node4)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node10 = cfg['nodes'][0]
            self.cfgBulider(node2, node10)
            self.cfgJoint(cfg)
        
        # alternativeNode is AST node foralternative field
        alternativeNode = self._astNode.child_by_field_name('alternative')
        if alternativeNode is not None:
            elseNode = None
            
        
            elseNode = Node('else', type='else_condition')

            alternativeSta = None
            alternativeSta = Statement(alternativeNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
            statementNode, ast, cfg = alternativeSta.handle()
            self.lastNodeListAdd(alternativeSta._lastNode)
            # if alternativeNode.type == 'if_statement':

            #     if len(alternativeSta._lastNode) == 1:
            #         # if alternativeSta._lastNode[0].type != 'break_statement' and alternativeSta._lastNode[0].type != 'continue_statement' and alternativeSta._lastNode[0].type != 'throw_statement':
            #         if alternativeSta._lastNode[0].type not in self._stopStatement:
            #             self.lastNodeListAdd(alternativeSta._lastNode)
            #     elif len(alternativeSta._lastNode) > 1:
            #         for n in alternativeSta._lastNode:
            #             # if n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
            #             if n.type not in self._stopStatement:
            #                 self._lastNode.append(n)
            #     else:
            #         self.lastNodeListAdd(alternativeSta._lastNode)
            #     self.lastNodeListAdd(alternativeSta._lastNode)
            # else:
            #     if the break_statement or continue_statement in else block, the break_statement or continue_statement will not connect to next statement
            #     self.lastNodeListAdd(alternativeSta._lastNode)

            self.levelNodeListAdd(alternativeSta._levelNode)
            self.continueLevelNodeListAdd(alternativeSta._continueLevelNode)
            self.ifLevelNodeListAdd(alternativeSta._ifLevelNode)
            self.throwLevelNodeListAdd(alternativeSta._throwNode)
            self.yieldLevelNodeListAdd(alternativeSta._yieldNode)
            if alternativeNode.type == 'if_statement':
                statementNode[0].label = elseLabel + statementNode[0].label
                

                if ast['nodes'] != []:
                    node6 = ast['nodes'][0]
                    node6.label = 'ifelse_'+ node6.label.split('_')[1]
                    # node6.type = 'elseif_condition'
                    self.astBulider(parent, node6)
                    self.astJoint(ast)

                if cfg['nodes'] != []:
                    node11 = cfg['nodes'][0]
                    node11.type = 'if_condition'
                    self.cfgBulider(node2, node11)
                    self.cfgJoint(cfg)

            elif alternativeNode.type == 'block':
                
                self._node.append(elseNode)

                node7 = Node('else_statement')
                self.astBulider(parent, node7)
                node8 = Node('condition')
                self.astBulider(node7, node8)
                self.astBulider(node8, elseNode)
                if ast['nodes'] != []:
                    node9 = ast['nodes'][0]
                    self.astBulider(node7, node9)
                    self.astJoint(ast)

                self.cfgBulider(node2, elseNode)
                if cfg['nodes'] != []:
                    node12 = cfg['nodes'][0]
                    
                    self.cfgBuiderForElseEdge(elseNode, node12)
                    self.cfgJoint(cfg)
                else:
                    self._lastNode.append(elseNode)
            else:
                self._node.append(elseNode)
                node7 = Node('else_statement')
                self.astBulider(parent, node7)
                node8 = Node('condition')
                self.astBulider(node7, node8)
                self.astBulider(node8, elseNode)
                if ast['nodes'] != []:
                    node9 = ast['nodes'][0]
                    self.astBulider(node7, node9)
                    self.astJoint(ast)

                self.cfgBulider(node2, elseNode)
                if cfg['nodes'] != []:
                    node12 = cfg['nodes'][0]
                    self.cfgBuiderForElseEdge(elseNode, node12)
                    self.cfgJoint(cfg)
            if statementNode != []:
                self._node.extend(statementNode)

        # else:
        #     if cfg['nodes'] != []:
        #         node13 = cfg['nodes'][0]
        #         self.cfgBulider(node2, node13)
        #         self.cfgJoint(cfg)
            
    def handleWhile(self):
        '''
        while_statement: $ => seq(
            'while',
            field('condition', $.condition),
            field('body', $.statement)
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        whileLabel = 'while '

        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        label = label + whileLabel
        # conditionNode is AST node for condition field
        conditionNode = self._astNode.child_by_field_name('condition')
        # label = label + self._code[conditionNode.start_byte:conditionNode.end_byte]
        label = label + conditionNode.text.decode('utf-8') + ' '

        node1 = Node('condition')
        self.astBulider(parent, node1)

        node2 = Node(label, type='while_condition')

        self.cfgBulider(node2)

        self._lastNode.append(node2)
        blockSta = self._astNode.child_by_field_name('body')
        
        # for child in blockSta.children:
        #     if child.type == 'break_statement':
        #         self._lastNode.remove(node2)

        self._node.append(node2)
        self.astBulider(node1, node2)
        # body field
        bodySta = None
        # bodyChild  = self._astNode.child_by_field_name('body').type
        bodySta = Statement(blockSta, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        
        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
            # self.checkContinueAndBreak(node2, cfg)

        if bodySta._continueLevelNode != []:
            for level, node in bodySta._continueLevelNode:
                if self._continueLevel == level:
                    self.cfgBuiderForContinueEdge(node, node2)

        
        node5 = bodySta._lastNode
        if node5 != []:
            for n in node5:
                # if n is not None and n.type != 'continue_statement' and n.type != 'break_statement' and n.type != 'throw_statement':
                if n is not None and n.type not in self._stopStatement:
                    self.cfgBulider(n, node2)
        
        node7 = self._levelNode
        if node7 != []:
            for level, n in node7:
                if level > self._level:
                    self.cfgBuiderForBreakEdge(n, node2)

        node6 = bodySta._lastIfNode
        if node6 is not None:
            self.cfgBulider(node6, node2)
        
    def handleFor(self):
        '''
        for_statement: $ => seq(
            'for', '(',
            choice(
                field('init', $.local_variable_declaration),
                seq(
                    commaSep(field('init', $.expression)),
                    ';'
                )
            ),
            field('condition', optional($.expression)), ';',
            commaSep(field('update', $.expression)), ')',
            field('body', $.statement)
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # forLabel = 'for ('

        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        # label = label + forLabel
        # # initNode is AST node of init field
        # initNode = self._astNode.children_by_field_name('init')
        # if initNode[0].type == 'local_variable_declaration':
        #     initLabel = self._code[initNode[0].start_byte:initNode[0].end_byte]
        #     label = label + initLabel + ' '
        # else:
        #     initLabelLsit = [self._code[node.start_byte:node.end_byte] for node in initNode]
        #     initLabel = ', '.join(initLabelLsit)
        #     label = label + initLabel 
        #     label = label + '; '
        # # conditionNode is AST node of condition field
        # conditionNode = self._astNode.child_by_field_name('condition')
        # if conditionNode is not None:
        #     conditonLabel = self._code[conditionNode.start_byte:conditionNode.end_byte]
        #     label = label + conditonLabel
        # label = label + '; '
        # # updateNode is AST node of all update field
        # updateNode = self._astNode.children_by_field_name('update')
        # updateLabelList = [self._code[node.start_byte:node.end_byte] for node in updateNode]
        # updateLabel = ', '.join(updateLabelList)
        # label = label + updateLabel
        # label = label + ')'

        
        node1 = Node('condition')
        self.astBulider(parent, node1)
        
        blockSta = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:blockSta.start_byte]
        node2 = Node(label, type = 'for_condition')

        self.cfgBulider(node2)

        self._lastNode.append(node2)
        # *********************
        # for child in blockSta.children:
        #     if child.type == 'break_statement':
        #         self._lastNode.remove(node2)
        # *********************
        self._node.append(node2)
        self.astBulider(node1, node2)
        # bodyNode is AST node of body field
        bodySta = None
        bodySta = Statement(blockSta, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)

        statementNode, ast, cfg = bodySta.handle()
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)
        
        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
            
        if bodySta._continueLevelNode != []:
            for level, node in bodySta._continueLevelNode:
                if self._continueLevel == level:
                    self.cfgBuiderForContinueEdge(node, node2)


        node5 = bodySta._lastNode
        if node5 != []:
            for n in node5:
                # if n is not None and n.type != 'continue_statement' and n.type != 'break_statement' and n.type != 'throw_statement':
                if n is not None and n.type not in self._stopStatement:
                    self.cfgBulider(n, node2)

        node7 = self._levelNode
        if node7 != []:
            for level, n in node7:
                if level > self._level:
                    self.cfgBuiderForBreakEdge(n, node2)

        

        node6 = bodySta._lastIfNode
        if node6 is not None:
            self.cfgBulider(node6, node2)
    def handleEnhanced(self):
        '''
        enhanced_for_statement: $ => seq(
            'for',
            '(',
            optional($.modifiers),
            field('type', $._unannotated_type),
            $._variable_declarator_id,
            ':',
            field('value', $.expression),
            ')',
            field('body', $.statement)
        ),

        _variable_declarator_id: $ => seq(
            field('name', choice($.identifier, $._reserved_identifier, $.underscore_pattern)),
            field('dimensions', optional($.dimensions))
        ),

        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        forLabel = 'for ('

        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        label = label + forLabel
        for child in self._astNode.children:
            if child.type == 'modifiers':
                # modifiersLabel = self._code[child.start_byte:child.end_byte]
                modifiersLabel = child.text.decode('utf-8')
                label = label + modifiersLabel + ' '
        
        # typeNode is AST node of type field
        typeNode = self._astNode.child_by_field_name('type')
        # typeLabel = self._code[typeNode.start_byte:typeNode.end_byte]
        typeLabel = typeNode.text.decode('utf-8')
        label = label + typeLabel + ' '
        # process _variable_declarator_id
        nameNode = self._astNode.child_by_field_name('name')
        # nameLabel = self._code[nameNode.start_byte:nameNode.end_byte]
        nameLabel = nameNode.text.decode('utf-8')
        label = label + nameLabel
        dimensionsNode = self._astNode.child_by_field_name('dimensions')
        if dimensionsNode is not None:
            # dimensionLabel = self._code[dimensionsNode.start_byte:dimensionsNode.end_byte]
            dimensionLabel = dimensionLabel.text.decode('utf-8')
            label = label + dimensionLabel
        label = label + ' : '
        # valueNode is AST node of value field
        valueNode = self._astNode.child_by_field_name('value')
        # valueLabel = self._code[valueNode.start_byte:valueNode.end_byte]
        valueLabel = valueNode.text.decode('utf-8')
        label = label + valueLabel
        label = label + ')'

        node1 = Node('condition')
        self.astBulider(parent, node1)
        node2 = Node(label, type = 'enhanced_for_condition')

        self.cfgBulider(node2)

        self._lastNode.append(node2)
        blockSta = self._astNode.child_by_field_name('body')
        # for child in blockSta.children:
        #     if child.type == 'break_statement':
        #         self._lastNode.remove(node2)
        self._node.append(node2)
        self.astBulider(node1, node2)
        # blockSta is AST node of body field
        bodySta = None
        bodySta = Statement(blockSta, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
            
        if bodySta._continueLevelNode != []:
            for level, node in bodySta._continueLevelNode:
                if self._continueLevel == level:
                    self.cfgBuiderForContinueEdge(node, node2)

        node5 = bodySta._lastNode
        if node5 != []:
            for n in node5:
                # if n is not None and n.type != 'continue_statement' and n.type != 'break_statement' and n.type != 'throw_statement':
                if n is not None and n.type not in self._stopStatement:
                    self.cfgBulider(n, node2)

        node7 = self._levelNode
        if node7 != []:
            for level, n in node7:
                if level > self._level:
                    self.cfgBuiderForBreakEdge(n, node2)

        node6 = bodySta._lastIfNode
        if node6 is not None:
            self.cfgBulider(node6, node2)

    def handleBlock(self):
        '''
        block: $ => seq(
            '{', repeat($.statement), '}'
        ),

        '''

        parent = Node(self._astNode.type)
        statementNode = []

        cfgs = []
        # we use this to handle break continue_statement, the break_statement can handle on the loop statement
        # but the continue only can handle on the block
        breakChild = []

        ifOrElseChild = []

        # ifNodeToContact = None

        lastBreakNodeForSwitch = []

        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        for i, child in enumerate(childList):
            # print(child.type)
            sta = None
            breakLevel = self._level
            continueLevel = self._continueLevel
            iflevel = self._ifLevel
            tryLevel = self._tryLevel
            yieldlevel = self._yieldLevel
            # self._levelStatement is break level statement
            if child.type in self._levelStatement:
                breakLevel = breakLevel + 1
            if child.type in self._continueLevelStatement:
                continueLevel = continueLevel + 1
            if child.type == 'if_statement':
                iflevel = iflevel + 1
            if child.type == 'try_statement':
                tryLevel = self._tryLevel + 1
            if child.type =='yield_statement':
                yieldlevel = self._yieldLevel + 1
            
            sta = Statement(child, self._code, breakLevel, iflevel, continueLevel, tryLevel, yieldlevel)
            statementNode, ast, cfg = sta.handle()

            # _levelNode is for break_statement
            if sta._levelNode != []:
                self.levelNodeListAdd(sta._levelNode)
            if sta._continueLevelNode != []:
                self.continueLevelNodeListAdd(sta._continueLevelNode)
            if sta._throwNode != []:
                self.throwLevelNodeListAdd(sta._throwNode)
            if sta._yieldNode != []:
                self.yieldLevelNodeListAdd(sta._yieldNode)

            if breakChild != []:
                for j, level, n in breakChild:
                    if i==j+1 and level == self._level + 1:
                        # self.cfgBulider(n, cfg['nodes'][0])
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])
                    # if i+1==len(childList) and i==j+1:
                    #     self.chageNodeLevel(n)

            if child.type == 'switch_expression':
                node16 = sta._levelNode
                for level, n in node16:
                    if level > self._level:
                        lastBreakNodeForSwitch.append((i, n))
                        # self.cfgBuiderForBreakEdge(n, lastChild[index+1][2])

            if lastBreakNodeForSwitch != []:
                for j, n in lastBreakNodeForSwitch:
                    if i==j+1:
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])

            # if continueChild != []:
            #     for j, level, n in continueChild:
            #         if i==j+1 and level == self._level + 1:
            #             self.cfgBulider(n, cfg['nodes'][0])

            if sta._ifLevelNode != []:
                self.ifLevelNodeListAdd(sta._ifLevelNode)
            if ifOrElseChild != []:
                elseOrIfNode = None
                for j, level, iflevel, n in ifOrElseChild:
                    if i==j+1 and iflevel == self._ifLevel and level == self._level:
                        elseOrIfNode = n
                if elseOrIfNode != None:
                    if elseOrIfNode.type == 'if_condition':
                        self.cfgBuiderForIfEdge(elseOrIfNode, cfg['nodes'][0])

            # in case for the nodes are unorder in self._cfg['nodes], add the child first
            self.cfgJoint(cfg)

            for n in cfg['nodes']:
                if n.type == 'identifier_break_statement':
                    self._identifierBreakNode = n

            # for n in cfg['nodes']:
            #     if n.type == 'break_statement':
            #         self.levelNodeAdd((self._level, n))
            if self._levelNode != []:
                for n in self._levelNode:
                    self.breakChildAdd(breakChild, i, n)


            for n in cfg['nodes']:
                if n.type == 'continue_statement':
                    self.continueLevelNodeAdd((self._continueLevel, n))


            if child.type == 'if_statement':
                for n in cfg['nodes']:
                    if n.type == 'else_condition' or n.type == 'if_condition':
                        self.ifLevelNodeAdd((self._level, self._ifLevel, n))


            if self._ifLevelNode != []:
                for n in self._ifLevelNode:
                    if n != [] :
                        if ifOrElseChild != []:
                            self.ifOrElseChildAdd(ifOrElseChild, i, n)
                        else:
                            ifOrElseChild.append((i, n[0], n[1], n[2]))

            ifNodeToContact = None     
            if child.type == 'if_statement' and self._ifLevelNode != []:
            # if i+1 == len(childList) and child.type == 'if_statement' and self._ifLevelNode != []:
                for n in self._ifLevelNode:
                    if n != [] and n[1] == self._ifLevel and n[0] == self._level:
                        if n[2].type != 'else_condition':
                            ifNodeToContact = n[2]
                for n in self._ifLevelNode:
                    if n != [] and n[1] == self._ifLevel and n[0] == self._level:
                        if n[2].type == 'else_condition':
                            ifNodeToContact = None
            self._lastIfNode = ifNodeToContact
            if ifNodeToContact != None:
                # if ifNodeToContact.type != 'else_condition':
                    sta._lastNode.append(ifNodeToContact)

            # lastChild = (child, cfg)

            if cfg['nodes'] != []:
                cfgs.append((cfg, sta))

            if statementNode != []:
                self._node.extend(statementNode)
            if ast['nodes'] != []:
                node2 = ast['nodes'][0]
                self.astBulider(parent, node2)
                self.astJoint(ast)

        # if ifNodeToContact != None:
        #     self._lastIfNode = ifNodeToContact
        
        contactNode = []
        if cfgs != []:
            for i, (cfg, sta) in enumerate(cfgs):
                contactNode.append((cfg, sta._lastNode, sta._astNode.type))
                if len(sta._lastNode) == 1:
                    # if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement' or sta._lastNode[0].type == 'throw_statement':
                    if sta._lastNode[0].type in self._stopStatement:
                        if sta._astNode.type in self._declarations:
                            continue
                        else:
                            break

        
        if contactNode != []:
            self._lastNode.extend(contactNode[-1][1])
            for i in range(len(contactNode)):
                if i+1 < len(contactNode):
                    for n in contactNode[i][1]:
                        # if n != None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                        if n != None and n.type not in self._stopStatement:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])
                        if n != None and n.type in self._stopStatement and contactNode[i][2] in self._declarations:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])
                    
                    

                

    def handleAssert(self):
        '''
        assert_statement: $ => choice(
            seq('assert', $.expression, ';'),
            seq('assert', $.expression, ':', $.expression, ';')
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        
        node1 = Node(label, type='assert_statement')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleDo(self):
        '''
        do_statement: $ => seq(
            'do',
            field('body', $.statement),
            'while',
            field('condition', $.parenthesized_expression),
            ';'
        ),
        '''
        parent = Node('do_statement')
        # label is source code of current node
        label = ''
        doLabel = 'do'
        whileLabel = 'while '

        # cfg nodes, these nodes are the child of the current node
        statementNode = []
        node4 = Node(doLabel, type = 'do_statement')

        self.cfgBulider(node4)

        self._node.append(node4)
        # body field
        bodySta = None
        blockSta = self._astNode.child_by_field_name('body')
        bodySta = Statement(blockSta, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node1 = ast['nodes'][0]
            self.astBulider(parent, node1)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node5 = cfg['nodes'][0]
            self.cfgBulider(node4, node5)
            self.cfgJoint(cfg)

        
        # conditionNode is AST node for condition field
        conditionNode = self._astNode.child_by_field_name('condition')
        label = label + whileLabel
        # label = label + self._code[conditionNode.start_byte:conditionNode.end_byte]
        label = label + conditionNode.text.decode('utf-8')
        label = label + ';'
    
        node2 = Node('condition')
        self.astBulider(parent, node2)
        node3 = Node(label, type = 'do_condition')
        self._lastNode.append(node3)
        existbreak = False
        for child in blockSta.children:
            if child.type == 'break_statement':
                existbreak = True
                self._lastNode.remove(node3)
        self._node.append(node3)
        self.astBulider(node2, node3)
        if existbreak == False:
            self.cfgBulider(node3, node4)

        if cfg['nodes'] == []:
            self.cfgBulider(node4, node3)

        if bodySta._continueLevelNode != []:
            for level, node in bodySta._continueLevelNode:
                if self._continueLevel == level:
                    self.cfgBuiderForContinueEdge(node, node3)

        node6 = bodySta._lastNode
        if node6 != []:
            for n in node6:
                # if n is not None and n.type != 'continue_statement' and n.type != 'break_statement' and n.type != 'throw_statement':
                if n is not None and n.type not in self._stopStatement:
                    self.cfgBulider(n, node3)

        node7 = self._levelNode
        if node7 != []:
            for level, n in node7:
                if level > self._level:
                    self.cfgBuiderForBreakEdge(n, node3)

        node8 = bodySta._lastIfNode
        if node8 is not None:
            self.cfgBulider(node8, node3)

    def handleBreak(self):
        '''
        break_statement: $ => seq('break', optional($.identifier), ';'),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        mark = 0
        for child in childList:
            if child.type == 'identifier':
                mark = 1
        if mark == 1:
            node1 = Node(label, type = 'identifier_break_statement')
        else:
            node1 = Node(label, type = 'break_statement')
            self.levelNodeAdd((self._level, node1))
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleContinue(self):
        '''
        continue_statement: $ => seq('continue', optional($.identifier), ';'),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        mark = 0
        for child in childList:
            if child.type == 'identifier':
                mark = 1
        if mark == 1:
            node1 = Node(label, type = 'identifier_continue_statement')
        else:
            node1 = Node(label, type = 'continue_statement')
            self.levelNodeAdd((self._continueLevel, node1))

        # node1 = Node(label, type = 'continue_statement')
        # self.continueLevelNodeAdd((self._continueLevel, node1))
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleReturn(self):
        '''
        return_statement: $ => seq(
            'return',
            optional($.expression),
            ';'
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type = 'return_statement')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleYield(self):
        '''
        yield_statement: $ => seq(
            'yield',
            $.expression,
            ';'
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type = 'yield_statement')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.yieldLevelNodeAdd((self._yieldLevel, node1))
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleSwitch(self):
        '''
        switch_expression: $ => seq(
            'switch',
            field('condition', $.parenthesized_expression),
            field('body', $.switch_block)
            ),

        switch_block: $ => seq(
            '{',
            choice(
            repeat($.switch_block_statement_group),
            repeat($.switch_rule)
            ),
            '}'
        ),

        switch_block_statement_group: $ => prec.left(seq(
            repeat1(seq($.switch_label, ':')),
            repeat($.statement),
        )),

        switch_rule: $ => seq(
            $.switch_label,
            '->',
            choice($.expression_statement, $.throw_statement, $.block)
        ),

        switch_label: $ => choice(
            seq('case',
                choice(
                $.pattern,
                commaSep1($.expression)
                ),
                optional($.guard)
            ),
            'default'
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        switchLabel = 'switch '
        
        # cfg nodes, these nodes are the child of the current node
        statementNode = []
        
        label = label + switchLabel
        # process condition field
        conditionNode = self._astNode.child_by_field_name('condition')
        # label = label + self._code[conditionNode.start_byte:conditionNode.end_byte]
        label = label + conditionNode.text.decode('utf-8')

        node1 = Node('condition')
        self.astBulider(parent, node1)
        node2 = Node(label, type = 'switch_condition')

        self.cfgBulider(node2)

        self.cfgBulider(node2)
        # self._lastNode = node2
        self._node.append(node2)
        self.astBulider(node1, node2)
        # process body field
        bodyNode = self._astNode.child_by_field_name('body')
        node3 = Node(bodyNode.type)
        self.astBulider(parent, node3)

        switchRuleLabelNodeList = []
        switchGroupLabelNodeList = []
        childList = [child for child in bodyNode.children if child.type not in self._ignoreStatement]
        lastChild = []
        groupLabelNodeList = []
        groupStatementNodeList = []
        
        if childList == []:
            self._lastNode.append(node2)
            return
        for i, child in enumerate(childList):
            # lastChild.clear()
            breakChild = []
            if child.type == 'switch_rule':
                
                node4 = Node(child.type)
                self.astBulider(node3, node4)
                # ruleLabel = self._code[child.start_byte:child.end_byte]
                # self._node.append(Node(ruleLabel))
                ruleLabel = ''
                label1 = ' -> '
                label2 = ''
                label3 = ''
                for n in child.children:
                    if n.type == 'switch_label':
                        # label2 = self._code[n.start_byte:n.end_byte]
                        label2 = n.text.decode('utf-8')
                        ruleLabel = label2 + label1

                    elif n.type == 'expression_statement' or n.type == 'throw_statement':
                        # label3 = self._code[n.start_byte:n.end_byte]
                        label3 = n.text.decode('utf-8')
                        ruleLabel = ruleLabel + label3

                        node6 = Node(n.type)
                        self.astBulider(node4, node6)
                        node7 = Node(ruleLabel, type='switch_label')
                        self._node.append(node7)
                        self.astBulider(node6, node7)

                        switchRuleLabelNodeList.append(node7)
                        self._switchLastNode.append(node7)
                        self.cfgBulider(node7)
                        self._lastNode.append(node7)
                    elif n.type == 'block':
                        # node8 = Node(n.type)
                        # self.astBulider(node3, node8)
                        node9 = Node(ruleLabel, type='switch_label')
                        self._node.append(node9)
                        self.astBulider(node4, node9)
                        switchRuleLabelNodeList.append(node9)
                        nSta = None
                        nSta = Statement(n, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                        statementNode, ast, cfg = nSta.handle()
                        self.lastNodeListAdd(nSta._lastNode)
                        self.levelNodeListAdd(nSta._levelNode)
                        self.continueLevelNodeListAdd(nSta._continueLevelNode)
                        self.ifLevelNodeListAdd(nSta._ifLevelNode)
                        self.throwLevelNodeListAdd(nSta._throwNode)
                        self.yieldLevelNodeListAdd(nSta._yieldNode)

                        if nSta._yieldNode != []:
                            for level, node in nSta._yieldNode:
                                if self._yieldLevel == level:
                                    self.cfgBuiderForYieldEdge(node, node2)

                        if statementNode != []:
                            self._node.extend(statementNode)

                        if ast['nodes'] != []:
                            node10 = ast['nodes'][0]
                            self.astBulider(node4, node10)
                            self.astJoint(ast)

                        if cfg['nodes'] != []:
                            node11 = cfg['nodes'][0]
                            self.cfgBulider(node9, node11)
                            self.cfgJoint(cfg)

                        # node12 = nSta._lastNode
                        # if node12 is not None:
                        #     self._switchLastNode.append(node12)
            

            if child.type == 'switch_block_statement_group':
                groupLabelStatement = []
                node11 = Node(child.type)
                self.astBulider(node3, node11)
                groupLabel = ''
                firstNode = None
                node13 = None
                block = []
                nSta = None
                cs = [c for c in child.children if c.type not in self._ignoreStatement]
                for j, n in enumerate(cs):
                    if n.type == 'switch_label':
                        # groupLabel = self._code[n.start_byte:n.end_byte] + ':'
                        groupLabel = n.text.decode('utf-8') + ':'

                        node12 = Node(n.type)
                        self.astBulider(node11, node12)
                        node13 = Node(groupLabel, type='switch_label')
                        self._node.append(node13)
                        self.astBulider(node12, node13)
                        switchGroupLabelNodeList.append(node13)
                        groupLabelNodeList.append((i, node13))
                        self.cfgBulider(node13)
                    elif n.type in self._statements:
                        
                        breakLevel = self._level
                        continueLevel = self._continueLevel
                        iflevel = self._ifLevel
                        # self._levelStatement is break level statement
                        if n.type in self._levelStatement:
                            breakLevel = breakLevel + 1
                        if n.type in self._continueLevelStatement:
                            continueLevel = continueLevel + 1
                        if n.type == 'if_statement':
                            iflevel = iflevel + 1

                        nSta = Statement(n, self._code, breakLevel, iflevel, continueLevel, self._tryLevel, self._yieldLevel)
                        block.append((n, nSta))
                        # statementNode, ast, cfg = nSta.handle()
                        # nSta.handleCaseBlock()
                        # self.levelNodeListAdd(nSta._levelNode)
                        # self.continueLevelNodeListAdd(nSta._continueLevelNode)
                        # self.ifLevelNodeListAdd(nSta._ifLevelNode)

                        # if breakChild != []:
                        #     for k, level, n in breakChild:
                        #         if j-1==k+1 and level == self._level + 1:
                        #             self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])
                                    
                        # if statementNode != []:
                        #     self._node.extend(statementNode)

                        # if ast['nodes'] != []:
                        #     node14 = ast['nodes'][0]
                        #     self.astBulider(node11, node14)
                        #     self.astJoint(ast)

                        # if cfg['nodes'] != []:
                        #     node15 = cfg['nodes'][0]
                        #     if firstNode == None:
                        #         firstNode = node15
                        #     self.cfgJoint(cfg)

                        # for n in cfg['nodes']:
                        #     if n.type == 'break_statement':
                        #         self.levelNodeAdd((self._level, n))
                        # if self._levelNode != []:
                        #     for n in self._levelNode:
                        #         self.breakChildAdd(breakChild, j-1, n)

                        # groupLabelStatement.append((i, nSta, cfg))
                caseBlockSta = Statement(None, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = caseBlockSta.handleCaseBlock(block, node11)
                self.levelNodeListAdd(caseBlockSta._levelNode)
                self.continueLevelNodeListAdd(caseBlockSta._continueLevelNode)
                self.ifLevelNodeListAdd(caseBlockSta._ifLevelNode)
                self.throwLevelNodeListAdd(caseBlockSta._throwNode)
                self.yieldLevelNodeListAdd(caseBlockSta._yieldNode)
                lastChild.append((i, caseBlockSta, node13))

                if statementNode != []:
                    self._node.extend(statementNode)

                if ast['nodes'] != []:
                    node14 = ast['nodes'][0]
                    # self.astBulider(node11, node14)
                    self.astJoint(ast)

                if cfg['nodes'] != []:
                    node15 = cfg['nodes'][0]
                    # if firstNode == None:
                    #     firstNode = node15
                    self.cfgBulider(node13, node15)
                    self.cfgJoint(cfg)
                # self.cfgBulider(node13, firstNode)
                # contactNode = []
                # if groupLabelStatement != []:
                #     lastSta = ()
                #     for index, (i, sta, cfg) in enumerate(groupLabelStatement):
                #         contactNode.append((cfg, sta._lastNode))
                #         lastSta = (i, sta._lastNode)
                #         if len(sta._lastNode) == 1:
                #             if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement':
                #                 break
                #     groupStatementNodeList.append(lastSta)
                # if contactNode != []:
                #     lastChild = contactNode[-1][1]
                #     for i in range(len(contactNode)):
                #         if i+1 < len(contactNode):
                #             for n in contactNode[i][1]:
                #                 if n != None and n.type != 'break_statement' and n.type != 'continue_statement':
                #                     self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])

        
        if lastChild != []:
            if lastChild[-1][1]._cfg['nodes'] != []:
                self.lastNodeListAdd(lastChild[-1][1]._lastNode)
            # self.lastNodeListAdd(lastChild[-1][1]._lastNode)
            else :
                self._lastNode.append(lastChild[-1][2])
        for index, blockSta, groupLabelNode in lastChild:
            if blockSta._lastNode != []:
                for n in blockSta._lastNode:
                    if n is not None and n.type not in self._stopStatement:
                        if index+1 < len(childList):
                            self.cfgBulider(n, lastChild[index+1][2])
            node16 = blockSta._levelNode
            if node16 != []:
                for level, n in node16:
                    if level > self._level:
                        if index+1 < len(childList):
                            self.cfgBuiderForBreakEdge(n, lastChild[index+1][2])
        # for index, node in groupStatementNodeList:
        #     for n in node:
        #         if n.type != 'break_statement' and n.type != 'continue_statement':
        #             if index+1 < len(groupLabelNodeList):
        #                 if groupLabelNodeList[index+1]:
        #                     for i, labelNode in groupLabelNodeList:
        #                         if index+1 == i:
        #                             self.cfgBulider(n, labelNode)
        # if len(lastChild) == 1:
        #     if lastChild[0].type != 'break_statement' and lastChild[0].type != 'continue_statement':
        #         self.lastNodeListAdd(lastChild)
        # elif len(lastChild) > 1:
        #     self.lastNodeListAdd(lastChild)

        if switchRuleLabelNodeList != []:
            self.cfgBulider(node2, switchRuleLabelNodeList[0])
            for i, node in enumerate(switchRuleLabelNodeList):
                if i+1 < len(switchRuleLabelNodeList):
                    self.cfgBulider(switchRuleLabelNodeList[i], switchRuleLabelNodeList[i+1])
        if switchGroupLabelNodeList != []:
            self.cfgBulider(node2, switchGroupLabelNodeList[0])
            for i, node in enumerate(switchGroupLabelNodeList):
                if i+1 < len(switchGroupLabelNodeList):
                    self.cfgBulider(switchGroupLabelNodeList[i], switchGroupLabelNodeList[i+1])
                # if i+1 == len(switchGroupLabelNodeList):
                #     self.cfgBulider(switchGroupLabelNodeList[i], node3)
    def handleCaseBlock(self, block, parentNode):
        
        statementNode = []

        cfgs = []

        breakChild = []

        ifOrElseChild = []

        # ifNodeToContact = None

        childList = [childs for childs, sta in block]

        lastBreakNodeForSwitch = []

        for i, (child, sta) in enumerate(block):
            # sta = None
            # breakLevel = self._level
            # continueLevel = self._continueLevel
            # iflevel = self._ifLevel
            # # self._levelStatement is break level statement
            # if child.type in self._levelStatement:
            #     breakLevel = breakLevel + 1
            # if child.type in self._continueLevelStatement:
            #     continueLevel = continueLevel + 1
            # if child.type == 'if_statement':
            #     iflevel = iflevel + 1
            
            # sta = Statement(child, self._code, breakLevel, iflevel, continueLevel)
            statementNode, ast, cfg = sta.handle()

            # _levelNode is for break_statement
            if sta._levelNode != []:
                self.levelNodeListAdd(sta._levelNode)
            if sta._continueLevelNode != []:
                self.continueLevelNodeListAdd(sta._continueLevelNode)
            if sta._throwNode != []:
                self.throwLevelNodeListAdd(sta._throwNode)
            if sta._yieldNode != []:
                self.yieldLevelNodeListAdd(sta._yieldNode)

            if breakChild != []:
                for j, level, n in breakChild:
                    if i==j+1 and level == self._level + 1:
                        # self.cfgBulider(n, cfg['nodes'][0])
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])
                    # if i+1==len(childList) and i==j+1:
                    #     self.chageNodeLevel(n)

            if child.type == 'switch_expression':
                node16 = sta._levelNode
                for level, n in node16:
                    if level > self._level:
                        lastBreakNodeForSwitch.append((i, n))
                        # self.cfgBuiderForBreakEdge(n, lastChild[index+1][2])

            if lastBreakNodeForSwitch != []:
                for j, n in lastBreakNodeForSwitch:
                    if i==j+1:
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])

            # if continueChild != []:
            #     for j, level, n in continueChild:
            #         if i==j+1 and level == self._level + 1:
            #             self.cfgBulider(n, cfg['nodes'][0])

            if sta._ifLevelNode != []:
                self.ifLevelNodeListAdd(sta._ifLevelNode)
            if ifOrElseChild != []:
                elseOrIfNode = None
                for j, level, iflevel, n in ifOrElseChild:
                    if i==j+1 and iflevel == self._ifLevel and level == self._level:
                        elseOrIfNode = n
                if elseOrIfNode != None:
                    if elseOrIfNode.type == 'if_condition':
                        self.cfgBuiderForIfEdge(elseOrIfNode, cfg['nodes'][0])

            # in case for the nodes are unorder in self._cfg['nodes], add the child first
            self.cfgJoint(cfg)

            for n in cfg['nodes']:
                if n.type == 'identifier_break_statement':
                    self._identifierBreakNode = n

            # for n in cfg['nodes']:
            #     if n.type == 'break_statement':
            #         self.levelNodeAdd((self._level, n))
            if self._levelNode != []:
                for n in self._levelNode:
                    self.breakChildAdd(breakChild, i, n)


            for n in cfg['nodes']:
                if n.type == 'continue_statement':
                    self.continueLevelNodeAdd((self._continueLevel, n))


            if child.type == 'if_statement':
                for n in cfg['nodes']:
                    if n.type == 'else_condition' or n.type == 'if_condition':
                        self.ifLevelNodeAdd((self._level, self._ifLevel, n))


            if self._ifLevelNode != []:
                for n in self._ifLevelNode:
                    if n != [] :
                        if ifOrElseChild != []:
                            self.ifOrElseChildAdd(ifOrElseChild, i, n)
                        else:
                            ifOrElseChild.append((i, n[0], n[1], n[2]))
                        
            ifNodeToContact = None      
            if child.type == 'if_statement' and self._ifLevelNode != []:
            # if i+1 == len(childList) and child.type == 'if_statement' and self._ifLevelNode != []:
                for n in self._ifLevelNode:
                    if n != [] and n[1] == self._ifLevel and n[0] == self._level:
                        if n[2].type != 'else_condition':
                            ifNodeToContact = n[2]
                for n in self._ifLevelNode:
                    if n != [] and n[1] == self._ifLevel and n[0] == self._level:
                        if n[2].type == 'else_condition':
                            ifNodeToContact = None
            self._lastIfNode = ifNodeToContact
            if ifNodeToContact != None:
                # if ifNodeToContact.type != 'else_condition':
                    sta._lastNode.append(ifNodeToContact)

            # lastChild = (child, cfg)

            if cfg['nodes'] != []:
                cfgs.append((cfg, sta))

            if statementNode != []:
                self._node.extend(statementNode)
            if ast['nodes'] != []:
                node2 = ast['nodes'][0]
                self.astBulider(parentNode, node2)
                self.astJoint(ast)

        # if ifNodeToContact != None:
        #     self._lastIfNode = ifNodeToContact
        
        contactNode = []
        if cfgs != []:
            for i, (cfg, sta) in enumerate(cfgs):
                contactNode.append((cfg, sta._lastNode, sta._astNode.type))
                if len(sta._lastNode) == 1:
                    # if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement' or sta._lastNode[0].type == 'throw_statement':
                    if sta._lastNode[0].type in self._stopStatement:
                        if sta._astNode.type in self._declarations:
                            continue
                        else:
                            break

        
        if contactNode != []:
            self._lastNode.extend(contactNode[-1][1])
            for i in range(len(contactNode)):
                if i+1 < len(contactNode):
                    for n in contactNode[i][1]:
                        # if n != None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                        if n != None and n.type not in self._stopStatement:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])
                        if n != None and n.type in self._stopStatement and contactNode[i][2] in self._declarations:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])
        
        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleSynchronized(self):
        '''
        synchronized_statement: $ => seq(
            'synchronized',
            $.parenthesized_expression,
            field('body', $.block)
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        synchronizedLabel = 'synchronized '
        
        # cfg nodes, these nodes are the child of the current node
        statementNode = []
        
        label = label + synchronizedLabel
        # process parenthesized_expression
        for child in self._astNode.children:
            if child.type == 'parenthesized_expression':
                # parenthesizedLabel = self._code[child.start_byte:child.end_byte]
                parenthesizedLabel = child.text.decode('utf-8')
                label = label + parenthesizedLabel + ' '

        node1 = Node('condition')
        self.astBulider(parent, node1)
        node2 = Node(label, type='synchronized_statement')

        self.cfgBulider(node2)

        self._node.append(node2)
        self.astBulider(node1, node2)
        # body field
        bodySta = None
        bodySta = Statement(self._astNode.child_by_field_name('body'), self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        # self._lastNode = bodySta._lastNode
        self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
        else:
            self._lastNode.append(node2)

    def handleLocalVariable(self):
        '''
        local_variable_declaration: $ => seq(
            optional($.modifiers),
            field('type', $._unannotated_type),
            $._variable_declarator_list,
            ';'
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')


        node1 = Node(label, type='local_variable_declaration')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleThrow(self):
        '''
        throw_statement: $ => seq('throw', $.expression, ';'),
        '''
        parent = Node(self._astNode.type)
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type='throw_statement')
        self.throwLevelNodeAdd((self._tryLevel, node1))
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

    def handleTry(self):
        '''
        try_statement: $ => seq(
            'try',
            field('body', $.block),
            choice(
                repeat1($.catch_clause),
                seq(repeat($.catch_clause), $.finally_clause)
            )
        ),

        catch_clause: $ => seq(
            'catch',
            '(',
            $.catch_formal_parameter,
            ')',
            field('body', $.block)
        ),

        finally_clause: $ => seq('finally', $.block),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        tryLabel = 'try'
        
        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        # try node
        label = label + tryLabel

        node1 = Node(label, type='try_statement')
        # self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)
        self.cfgBulider(node1)
        # body field
        bodySta = None
        bodySta = Statement(self._astNode.child_by_field_name('body'), self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        lastNode = []
        if cfg['nodes'] != []:
            lastNode = bodySta._lastNode
        else :
            lastNode.append(node1)
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node2 = ast['nodes'][0]
            self.astBulider(parent, node2)
            self.astJoint(ast)
        if cfg['nodes'] != []:
            node11 = cfg['nodes'][0]
            self.cfgBulider(node1, node11)
            self.cfgJoint(cfg)
        throwNode = []
        if self._throwNode != []:
            for n in self._throwNode:
                if self._tryLevel == n[0]:
                    throwNode.append(n[1])

        # process catch_clause and finally_clause
        catchFinallyNode = []
        catchLastNode = []
        for child in self._astNode.children:
            if child.type == 'catch_clause':
                catchLabel = 'catch ('
                # process catch_formal_parameter
                for n in child.children:
                    if n.type == 'catch_formal_parameter':
                        # parameterLabel = self._code[n.start_byte:n.end_byte]
                        parameterLabel = n.text.decode('utf-8')
                        catchLabel = catchLabel + parameterLabel
                catchLabel = catchLabel + ')'
            

                node3 = Node('condition')
                self.astBulider(parent, node3)
                node4 = Node(catchLabel, type='caseStatement')
                self._node.append(node4)
                self.astBulider(node3, node4)
                

                catchFinallyNode.append(node4)
                # body field
                bodySta = None
                bodySta = Statement(child.child_by_field_name('body'), self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = bodySta.handle()
                # self.lastNodeListAdd(bodySta._lastNode)
                self.levelNodeListAdd(bodySta._levelNode)
                self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                self.throwLevelNodeListAdd(bodySta._throwNode)
                self.yieldLevelNodeListAdd(bodySta._yieldNode)
                if bodySta._lastNode != []:
                    catchLastNode.extend(bodySta._lastNode)
                else:
                    catchLastNode.append(node4)
                # catchLastNode.extend(bodySta._lastNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node5 = ast['nodes'][0]
                    self.astBulider(parent, node5)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    node9 = cfg['nodes'][0]
                    self.cfgBulider(node4, node9)
                    self.cfgJoint(cfg)
                
            if child.type == 'finally_clause':
                finallyLabel = 'finally'
                node6 = Node('condition')
                self.astBulider(parent, node6)
                node7 = Node(finallyLabel, type='finallyStatement')
                self._node.append(node7)
                self.astBulider(node6, node7)
                catchFinallyNode.append(node7)
                for n in child.children:
                    if n.type == 'block':
                        bodySta = None
                        bodySta = Statement(n, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                        statementNode, ast, cfg = bodySta.handle()
                        if bodySta._lastNode != []:
                            self.lastNodeListAdd(bodySta._lastNode)
                        else:
                            self._lastNode.append(node7)
                        # self.lastNodeListAdd(bodySta._lastNode)
                        self.levelNodeListAdd(bodySta._levelNode)
                        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                        self.throwLevelNodeListAdd(bodySta._throwNode)
                        self.yieldLevelNodeListAdd(bodySta._yieldNode)
                        # catchLastNode.extend(bodySta._lastNode)
                        if statementNode != []:
                            self._node.extend(statementNode)
                        if ast['nodes'] != []:
                            node8 = ast['nodes'][0]
                            self.astBulider(parent, node8)
                            self.astJoint(ast)
                        if cfg['nodes'] != []:
                            node10 = cfg['nodes'][0]
                            self.cfgBulider(node7, node10)
                            self.cfgJoint(cfg)

        if throwNode != []:
            for n in throwNode:
                self.cfgBuiderForThrowEdge(n, catchFinallyNode[0])
        finallyNode = None
        if catchFinallyNode != []:
            if lastNode != []:
                for n in lastNode:
                    # if n is not None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                    if n is not None and n.type not in self._stopStatement:
                        self.cfgBulider(n, catchFinallyNode[0])
            for i, node in enumerate(catchFinallyNode):
                if i+1 < len(catchFinallyNode):
                    self.cfgBulider(node, catchFinallyNode[i+1])

            if catchFinallyNode[-1].type == 'finallyStatement':
                finallyNode = catchFinallyNode[-1]

        if finallyNode != None:
            for lastNode in catchLastNode:
                # if lastNode != None and lastNode.type != 'break_statement' and lastNode.type != 'continue_statement' and lastNode.type != 'throw_statement':
                if lastNode != None and lastNode.type not in self._stopStatement:
                    self.cfgBulider(lastNode, finallyNode)
        else:
            for lastNode in catchLastNode:
                # self.lastNodeListAdd(lastNode)
                self._lastNode.append(lastNode)
            

    def handleTryWithResources(self):
        '''
        try_with_resources_statement: $ => seq(
            'try',
            field('resources', $.resource_specification),
            field('body', $.block),
            repeat($.catch_clause),
            optional($.finally_clause)
        ),

        resource_specification: $ => seq(
            '(', sep1($.resource, ';'), optional(';'), ')'
        ),

        resource: $ => choice(
            seq(
                optional($.modifiers),
                field('type', $._unannotated_type),
                $._variable_declarator_id,
                '=',
                field('value', $.expression)
            ),
            $.identifier,
            $.field_access
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        tryLabel = 'try'
        
        # cfg nodes, these nodes are the child of the current node
        statementNode = []

        # try node
        label = label + tryLabel
        

        node1 = Node(label)
        # self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)
        self.cfgBulider(node1)
        # process resources field
        resourcesNode = self._astNode.child_by_field_name('resources')

        node9 = Node(resourcesNode.type)
        self.astBulider(parent, node9)
        resourceCfgNode = []
        for child in resourcesNode.children:
            if child.type == 'resource':
                # resourceLabel = self._code[child.start_byte:child.end_byte]
                resourceLabel = child.text.decode('utf-8')
                node10 = Node(resourceLabel)
                resourceCfgNode.append(node10)
                self._node.append(node10)
                self.astBulider(node9, node10)
        
        for i, node in enumerate(resourceCfgNode):
            if i+1 < len(resourceCfgNode):
                self.cfgBulider(node, resourceCfgNode[i+1])
        
        lastResourceNode = None
        if resourceCfgNode != []:
            self.cfgBulider(node1, resourceCfgNode[0])
            lastResourceNode = resourceCfgNode[-1]
        # body field
        bodySta = None
        bodySta = Statement(self._astNode.child_by_field_name('body'), self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        lastNode = []
        if cfg['nodes'] != []:
            lastNode = bodySta._lastNode
        else :
            lastNode.append(lastResourceNode)
        self.levelNodeListAdd(bodySta._levelNode)
        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        self.throwLevelNodeListAdd(bodySta._throwNode)
        self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node2 = ast['nodes'][0]
            self.astBulider(parent, node2)
            self.astJoint(ast)
        if cfg['nodes'] != []:
            node11 = cfg['nodes'][0]
            self.cfgBulider(lastResourceNode, node11)
            self.cfgJoint(cfg)
        throwNode = []
        if self._throwNode != []:
            for n in self._throwNode:
                if self._tryLevel == n[0]:
                    throwNode.append(n[1])

        catchFinallyNode = []
        catchLastNode = []
        # process catch_clause and finally_clause
        for child in self._astNode.children:
            if child.type == 'catch_clause':
                catchLabel = 'catch ('
                # process catch_formal_parameter
                for n in child.children:
                    if n.type == 'catch_formal_parameter':
                        # parameterLabel = self._code[n.start_byte:n.end_byte]
                        parameterLabel = n.text.decode('utf-8')
                        catchLabel = catchLabel + parameterLabel
                catchLabel = catchLabel + ')'
                
                node3 = Node('condition')
                self.astBulider(parent, node3)
                node4 = Node(catchLabel, type='caseStatement')
                self._node.append(node4)
                self.astBulider(node3, node4)

                catchFinallyNode.append(node4)
                # body field
                bodySta = None
                bodySta = Statement(child.child_by_field_name('body'), self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = bodySta.handle()
                self.levelNodeListAdd(bodySta._levelNode)
                self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                self.throwLevelNodeListAdd(bodySta._throwNode)
                self.yieldLevelNodeListAdd(bodySta._yieldNode)
                if bodySta._lastNode != []:
                    catchLastNode.extend(bodySta._lastNode)
                else:
                    catchLastNode.append(node4)
                # catchLastNode.extend(bodySta._lastNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node5 = ast['nodes'][0]
                    self.astBulider(parent, node5)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    node9 = cfg['nodes'][0]
                    self.cfgBulider(node4, node9)
                    self.cfgJoint(cfg)
            if child.type == 'finally_clause':
                finallyLabel = 'finally'
                node6 = Node('condition')
                self.astBulider(parent, node6)
                node7 = Node(finallyLabel, type='finallyStatement')
                self._node.append(node7)
                self.astBulider(node6, node7)
                catchFinallyNode.append(node7)
                for n in child.children:
                    if n.type == 'block':
                        bodySta = None
                        bodySta = Statement(n, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                        statementNode, ast, cfg = bodySta.handle()
                        if bodySta._lastNode != []:
                            self.lastNodeListAdd(bodySta._lastNode)
                        else:
                            self._lastNode.append(node7)
                        # self.lastNodeListAdd(bodySta._lastNode)
                        self.levelNodeListAdd(bodySta._levelNode)
                        self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                        self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                        self.throwLevelNodeListAdd(bodySta._throwNode)
                        self.yieldLevelNodeListAdd(bodySta._yieldNode)
                        if statementNode != []:
                            self._node.extend(statementNode)
                        if ast['nodes'] != []:
                            node8 = ast['nodes'][0]
                            self.astBulider(parent, node8)
                            self.astJoint(ast)
                        if cfg['nodes'] != []:
                            node10 = cfg['nodes'][0]
                            self.cfgBulider(node7, node10)
                            self.cfgJoint(cfg)

        if throwNode != [] and catchFinallyNode != []:
            for n in throwNode:
                self.cfgBuiderForThrowEdge(n, catchFinallyNode[0])
        finallyNode = None
        if catchFinallyNode != []:
            if lastNode != []:
                for n in lastNode:
                    # if n is not None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                    if n is not None and n.type not in self._stopStatement:
                        self.cfgBulider(n, catchFinallyNode[0])
            for i, node in enumerate(catchFinallyNode):
                if i+1 < len(catchFinallyNode):
                    self.cfgBulider(node, catchFinallyNode[i+1])

            if catchFinallyNode[-1].type == 'finallyStatement':
                finallyNode = catchFinallyNode[-1]
        else:
            self._lastNode.append(lastResourceNode)
        
        if finallyNode != None:
            for lastNode in catchLastNode:
                if lastNode != None:
                    self.cfgBulider(lastNode, finallyNode)
        else:
            for n in catchLastNode:
                self._lastNode.append(n)

    def handleClassDeclaration(self):
        '''
        class_declaration: $ => seq(
            optional($.modifiers),
            'class',
            field('name', $.identifier),
            optional(field('type_parameters', $.type_parameters)),
            optional(field('superclass', $.superclass)),
            optional(field('interfaces', $.super_interfaces)),
            optional(field('permits', $.permits)),
            field('body', $.class_body),
        ),
        '''

        parent = Node('class')
        
        label = ''
        classBodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:classBodyNode.start_byte]


        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        # for child in classBodyNode.children:
        #     print(child.type)
        self.astBulider(parent, node1)
        self.astBulider(node1, node2)        

        bodySta = None
        bodySta = Statement(classBodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)

        
        
        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleClassBody(self, p=None):
        '''
        class_body: $ => seq(
            '{',
            repeat($._class_body_declaration),
            '}',
        ),

        _class_body_declaration: $ => choice(
            $.field_declaration,
            $.record_declaration,
            $.method_declaration,
            $.compact_constructor_declaration, // For records.
            $.class_declaration,
            $.interface_declaration,
            $.annotation_type_declaration,
            $.enum_declaration,
            $.block,
            $.static_initializer,
            $.constructor_declaration,
            ';',
        ),
        '''
        parent=Node('body')
        if p != None:
            parent = p
        # label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        cfgs = []
        breakNodes = []
        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        for i, child in enumerate(childList):
            if child.type == 'field_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleFieldDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                # self.continueLevelNodeListAdd(fieldSta._continueLevelNode)
                # self.ifLevelNodeListAdd(fieldSta._ifLevelNode)
                # self.throwLevelNodeListAdd(fieldSta._throwNode)
                # self.yieldLevelNodeListAdd(fieldSta._yieldNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'record_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleRecordDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'method_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleMethodDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'compact_constructor_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleCompactConstructorDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'class_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleClassDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'interface_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleInterfaceDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'annotation_type_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleAnnotationTypeDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'enum_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleEnumDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'block':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handle()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'static_initializer':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleStaticInitializer()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'constructor_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleConstructorDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
        
        if cfgs != [] and breakNodes != []:
            for i, (cfg, sta) in enumerate(cfgs):
                for level, n in breakNodes:
                    if level + 1 == i:
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])
        
        contactNode = []
        if cfgs != []:
            for i, (cfg, sta) in enumerate(cfgs):
                contactNode.append((cfg, sta._lastNode))
                if len(sta._lastNode) == 1:
                    # if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement' or sta._lastNode[0].type == 'throw_statement':
                    if sta._lastNode[0].type in self._stopStatement:
                        break

        
        if contactNode != []:
            self._lastNode.extend(contactNode[-1][1])
            for i in range(len(contactNode)):
                if i+1 < len(contactNode):
                    for n in contactNode[i][1]:
                        # if n != None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                        if n != None and n.type not in self._stopStatement:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])

        return (self.getNodes(), self.getAst(), self.getCfg())
        
    def handleFieldDeclaration(self):
        '''
        field_declaration: $ => seq(
            optional($.modifiers),
            field('type', $._unannotated_type),
            $._variable_declarator_list,
            ';'
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type='field_declaration')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleRecordDeclaration(self):
        '''
        record_declaration: $ => seq(
            optional($.modifiers),
            'record',
            field('name', $.identifier),
            field('components', $.record_components),
            optional(field('body', $.class_body))
        ),
        '''

        parent = Node('record')
        
        label = ''
        classBodyNode = self._astNode.child_by_field_name('body')

        # label = self._code[self._astNode.start_byte:classBodyNode.start_byte]
        if classBodyNode == None:
            # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
            label = self._astNode.text.decode('utf-8')
        else:
            label = self._code[self._astNode.start_byte:classBodyNode.start_byte]
        node1 = Node(self._astNode.type)
        node2 = Node(label)
        self.cfgBulider(node2)
        # for child in classBodyNode.children:
        #     print(child.type)
        self.astBulider(parent, node1)
        self.astBulider(node1, node2)  
        if classBodyNode == None:
            self._lastNode.append(node2)
            
            return (self.getNodes(), self.getAst(), self.getCfg())  

        bodySta = None
        bodySta = Statement(classBodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)

        return (self.getNodes(), self.getAst(), self.getCfg())   

    def handleMethodDeclaration(self):
        '''
        method_declaration: $ => seq(
            optional($.modifiers),
            $._method_header,
            choice(field('body', $.block), ';'),
        ),
        '''

        parent = Node('method')
        
        label = ''
        bodyNode = self._astNode.child_by_field_name('body')
        if bodyNode == None:
            # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
            label = self._astNode.text.decode('utf-8')
        else:
            label = self._code[self._astNode.start_byte:bodyNode.start_byte]


        node1 = Node(self._astNode.type)
        node2 = Node(label)
        # if the block is empty
        if self._startMethod == False:   
            self.cfgBulider(node2)
        else:
            self.cfgBulider(parent)

        if self._startMethod == False:
            self.astBulider(parent, node1)
            self.astBulider(node1, node2) 
        if bodyNode == None:
            self.cfgBulider(node2)
            self._lastNode.append(node2)
            return (self.getNodes(), self.getAst(), self.getCfg())
        
        bodySta = None
        bodySta = Statement(bodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        # if self._startMethod == False:   
        #     self._lastNode.append(node2)
        # else:
        #     self._lastNode.append(parent)
        # self._lastNode.append(node2)
        self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            if self._startMethod == False:
                self.cfgBulider(node2, node4)
            else:
                self.cfgBulider(parent, node4)
            self.cfgJoint(cfg)
        
        # node5 = bodySta._lastNode
        # if node5 != []:
        #     for n in node5:
        #         if n is not None and n.type not in self._stopStatement:
        #             if self._startMethod == False:
        #                 self.cfgBulider(n, node2)
        #             else:
        #                 self.cfgBulider(n, parent)
        #         if n is not None and n.type == 'return_statement':
        #             if self._startMethod == False:
        #                 self.cfgBuiderForReturnEdge(n, node2)
        #             else:
        #                 self.cfgBuiderForReturnEdge(n, parent)
        # for node in cfg['nodes']:
        #     if node.type == 'return_statement':
        #         if self._startMethod == False:
        #             self.cfgBuiderForReturnEdge(node, node2)
        #         else:
        #             self.cfgBuiderForReturnEdge(node, parent)
        # for node in cfg['nodes']:
        #     # print(node.type)
        #     if node.type == 'break_statement':
        #         if self._startMethod == False:
        #             self.cfgBuiderForBreakEdge(node, node2)
        #         else:
        #             self.cfgBuiderForBreakEdge(node, parent)

        
        # for node in cfg['nodes']:
        #     if node.type == 'return_statement':
        #         if not self.existReturnEdge(node) and node not in self._lastNode:
        #             self._lastNode.append(node)

        # for node in cfg['nodes']:
        #     # print(node.type)
        #     if node.type == 'break_statement':
        #         if self._startMethod == False:
        #             self.cfgBuiderForBreakEdge(node, node2)
        #         else:
        #             self.cfgBuiderForBreakEdge(node, parent)

        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleCompactConstructorDeclaration(self):
        '''
        compact_constructor_declaration: $ => seq(
            optional($.modifiers),
            field('name', $.identifier),
            field('body', $.block)
        ),
        '''
        parent = Node('compact_constructor')
        
        label = ''
        bodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:bodyNode.start_byte]

        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        self.astBulider(parent, node1)
        self.astBulider(node1, node2) 

        bodySta = None
        bodySta = Statement(bodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handle()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)

        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleInterfaceDeclaration(self):
        '''
        interface_declaration: $ => seq(
            optional($.modifiers),
            'interface',
            field('name', $.identifier),
            field('type_parameters', optional($.type_parameters)),
            optional($.extends_interfaces),
            optional(field('permits', $.permits)),
            field('body', $.interface_body),
        ),
        '''

        parent = Node('interface')

        label = ''
        classBodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:classBodyNode.start_byte]

        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        self.astBulider(parent, node1)
        self.astBulider(node1, node2)        

        bodySta = None
        bodySta = Statement(classBodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handleInterfaceBody()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
        
        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleInterfaceBody(self):
        '''
        interface_body: $ => seq(
            '{',
            repeat(choice(
                $.constant_declaration,
                $.enum_declaration,
                $.method_declaration,
                $.class_declaration,
                $.interface_declaration,
                $.record_declaration,
                $.annotation_type_declaration,
                ';',
            )),
            '}',
        ),
        '''
        parent = Node('interface_body')
        
        # label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        cfgs = []
        breakNodes = []
        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        for i, child in enumerate(childList):
            
            if child.type == 'constant_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleConstantDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                # self.levelNodeListAdd(fieldSta._levelNode)
                # self.continueLevelNodeListAdd(fieldSta._continueLevelNode)
                # self.ifLevelNodeListAdd(fieldSta._ifLevelNode)
                # self.throwLevelNodeListAdd(fieldSta._throwNode)
                # self.yieldLevelNodeListAdd(fieldSta._yieldNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'enum_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleEnumDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'method_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleMethodDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'class_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleClassDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'interface_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleInterfaceDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'record_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleRecordDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'annotation_type_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleAnnotationTypeDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)

        if cfgs != [] and breakNodes != []:
            for i, (cfg, sta) in enumerate(cfgs):
                for level, n in breakNodes:
                    if level + 1 == i:
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])

        contactNode = []
        if cfgs != []:
            for i, (cfg, sta) in enumerate(cfgs):
                contactNode.append((cfg, sta._lastNode))
                if len(sta._lastNode) == 1:
                    # if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement' or sta._lastNode[0].type == 'throw_statement':
                    if sta._lastNode[0].type in self._stopStatement:
                        break

        
        if contactNode != []:
            self._lastNode.extend(contactNode[-1][1])
            for i in range(len(contactNode)):
                if i+1 < len(contactNode):
                    for n in contactNode[i][1]:
                        # if n != None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                        if n != None and n.type not in self._stopStatement:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])
        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleConstantDeclaration(self):
        '''
        constant_declaration: $ => seq(
            optional($.modifiers),
            field('type', $._unannotated_type),
            $._variable_declarator_list,
            ';',
        ),

        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type='constant_declaration')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

        return (self.getNodes(), self.getAst(), self.getCfg())
    


    def handleAnnotationTypeDeclaration(self):
        '''
        annotation_type_declaration: $ => seq(
            optional($.modifiers),
            '@interface',
            field('name', $.identifier),
            field('body', $.annotation_type_body),
        ),
        '''
        parent = Node('annotation')

        label = ''
        classBodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:classBodyNode.start_byte]

        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        # for child in classBodyNode.children:
        #     print(child.type)
        self.astBulider(parent, node1)
        self.astBulider(node1, node2)        

        bodySta = None
        bodySta = Statement(classBodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handleAnnotationTypeBody()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)
        
        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleAnnotationTypeBody(self):
        '''
        annotation_type_body: $ => seq(
            '{',
            repeat(choice(
                $.annotation_type_element_declaration,
                $.constant_declaration,
                $.class_declaration,
                $.interface_declaration,
                $.enum_declaration,
                $.annotation_type_declaration,
                ';',
            )),
            '}',
        ),
        '''
        parent = Node('annotation_body')
        cfgs = []
        breakNodes = []
        childList = [child for child in self._astNode.children if child.type not in self._ignoreStatement]
        for i, child in enumerate(childList):
            if child.type == 'annotation_type_element_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleAnnotationTypeElementDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                # self.continueLevelNodeListAdd(fieldSta._continueLevelNode)
                # self.ifLevelNodeListAdd(fieldSta._ifLevelNode)
                # self.throwLevelNodeListAdd(fieldSta._throwNode)
                # self.yieldLevelNodeListAdd(fieldSta._yieldNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'constant_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleConstantDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'class_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleClassDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'interface_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleInterfaceDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'enum_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleEnumDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)
            if child.type == 'annotation_type_declaration':
                fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = fieldSta.handleAnnotationTypeDeclaration()
                self.levelNodeListAdd(fieldSta._levelNode)
                node7 = fieldSta._levelNode
                if node7 != []:
                    for level, n in node7:
                        breakNodes.append((i, n))
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node1 = ast['nodes'][0]
                    self.astBulider(parent, node1)
                    self.astJoint(ast)
                if cfg['nodes'] != []:
                    if cfg['nodes'] != []:
                        cfgs.append((cfg, fieldSta))
                    # node2 = cfg['nodes'][0]
                    # self.cfgBulider(node1, node2)
                    self.cfgJoint(cfg)

        if cfgs != [] and breakNodes != []:
            for i, (cfg, sta) in enumerate(cfgs):
                for level, n in breakNodes:
                    if level + 1 == i:
                        self.cfgBuiderForBreakEdge(n, cfg['nodes'][0])
                        
        contactNode = []
        if cfgs != []:
            for i, (cfg, sta) in enumerate(cfgs):
                contactNode.append((cfg, sta._lastNode))
                if len(sta._lastNode) == 1:
                    # if sta._lastNode[0].type == 'break_statement' or sta._lastNode[0].type == 'continue_statement' or sta._lastNode[0].type == 'throw_statement':
                    if sta._lastNode[0].type in self._stopStatement:
                        break

        
        if contactNode != []:
            self._lastNode.extend(contactNode[-1][1])
            for i in range(len(contactNode)):
                if i+1 < len(contactNode):
                    for n in contactNode[i][1]:
                        # if n != None and n.type != 'break_statement' and n.type != 'continue_statement' and n.type != 'throw_statement':
                        if n != None and n.type not in self._stopStatement:
                            self.cfgBulider(n, contactNode[i+1][0]['nodes'][0])

        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleAnnotationTypeElementDeclaration(self):
        '''
        annotation_type_element_declaration: $ => seq(
            optional($.modifiers),
            field('type', $._unannotated_type),
            field('name', choice($.identifier, $._reserved_identifier)),
            '(', ')',
            field('dimensions', optional($.dimensions)),
            optional($._default_value),
            ';',
        ),
        '''
        parent = Node(self._astNode.type)
        # label is source code of current node
        label = ''
        # label = self._code[self._astNode.start_byte:self._astNode.end_byte]
        label = self._astNode.text.decode('utf-8')

        node1 = Node(label, type='annotation_type_element_declaration')
        self._lastNode.append(node1)
        self._node.append(node1)
        self.astBulider(parent, node1)

        self.cfgBulider(node1)

        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleEnumDeclaration(self):
        '''
        enum_declaration: $ => seq(
            optional($.modifiers),
            'enum',
            field('name', $.identifier),
            field('interfaces', optional($.super_interfaces)),
            field('body', $.enum_body),
        ),
        '''
        parent = Node('enum')

        label = ''
        bodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:bodyNode.start_byte]

        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        self.astBulider(parent, node1)
        self.astBulider(node1, node2) 

        bodySta = None
        bodySta = Statement(bodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handleEnumBody()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)


        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleEnumBody(self):
        '''
        enum_body: $ => seq(
            '{',
            commaSep($.enum_constant),
            optional(','),
            optional($.enum_body_declarations),
            '}',
        ),

        enum_body_declarations: $ => seq(
            ';',
            repeat($._class_body_declaration),
        ),

        enum_constant: $ => (seq(
            optional($.modifiers),
            field('name', $.identifier),
            field('arguments', optional($.argument_list)),
            field('body', optional($.class_body)),
        )),
        '''
        parent = Node('enum_body')
        node1 = Node('enum_constant')
        self.astBulider(parent, node1)

        enumConstantlabel = ''
        enumConstantlabel1 =''
        for child in self._astNode.children:
            if child.type == 'enum_constant':
                # enumConstantlabel1 = enumConstantlabel1 + self._code[child.start_byte:child.end_byte] + ','
                enumConstantlabel1 = enumConstantlabel1 + child.text.decode('utf-8') + ','
        if enumConstantlabel1[:-1] != '':
            enumConstantlabel = enumConstantlabel1[:-1] + ';'
        else:
            return (self.getNodes(), self.getAst(), self.getCfg())
        node2 = Node(enumConstantlabel)
        self.astBulider(node1, node2)

        mark = 0
        for child in self._astNode.children:
            if child.type == 'enum_body_declarations':
                mark = 1
        if mark == 0:
            self._lastNode.append(node2)
            self.cfgBulider(node2)
            return (self.getNodes(), self.getAst(), self.getCfg())

        for child in self._astNode.children:
            if child.type == 'enum_body_declarations':
                if child.text == b';':
                    self._lastNode.append(node2)
                    self.cfgBulider(node2)
                    return (self.getNodes(), self.getAst(), self.getCfg())
                else:
                    bodySta = None
                    bodySta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                    statementNode, ast, cfg = bodySta.handleClassBody(parent)
                    self.lastNodeListAdd(bodySta._lastNode)
                    self.levelNodeListAdd(bodySta._levelNode)
                    # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                    # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                    # self.throwLevelNodeListAdd(bodySta._throwNode)
                    # self.yieldLevelNodeListAdd(bodySta._yieldNode)
                    if statementNode != []:
                        self._node.extend(statementNode)
                    if ast['nodes'] != []:
                        # node3 = ast['nodes'][0]
                        # self.astBulider(parent, node3)
                        self.astJoint(ast)

                    if cfg['nodes'] != []:
                        node4 = cfg['nodes'][0]
                        self.cfgBulider(node2, node4)
                        self.cfgJoint(cfg)

        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleStaticInitializer(self):
        '''
        static_initializer: $ => seq(
            'static',
            $.block,
        ),
        '''
        parent = Node('static_initializer')
        label = 'static'
        node1 = Node(label)

        self.cfgBulider(node1)

        self.astBulider(parent, node1)
        for child in self._astNode.children:
            if child.type == 'block':
                bodySta = None
                bodySta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                statementNode, ast, cfg = bodySta.handle()
                if cfg['nodes'] != []:
                    self.lastNodeListAdd(bodySta._lastNode)
                else:
                    self._lastNode.append(node1)
                # self.lastNodeListAdd(bodySta._lastNode)
                self.levelNodeListAdd(bodySta._levelNode)
                # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
                # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
                # self.throwLevelNodeListAdd(bodySta._throwNode)
                # self.yieldLevelNodeListAdd(bodySta._yieldNode)
                if statementNode != []:
                    self._node.extend(statementNode)
                if ast['nodes'] != []:
                    node2 = ast['nodes'][0]
                    self.astBulider(parent, node2)
                    self.astJoint(ast)

                if cfg['nodes'] != []:
                    node3 = cfg['nodes'][0]
                    self.cfgBulider(node1, node3)
                    self.cfgJoint(cfg)

        return (self.getNodes(), self.getAst(), self.getCfg())

    def handleConstructorDeclaration(self):
        '''
        constructor_declaration: $ => seq(
            optional($.modifiers),
            $._constructor_declarator,
            optional($.throws),
            field('body', $.constructor_body),
        ),
        '''
        parent = Node('constructor')
        label = ''
        bodyNode = self._astNode.child_by_field_name('body')
        label = self._code[self._astNode.start_byte:bodyNode.start_byte]

        node1 = Node(self._astNode.type)
        node2 = Node(label)

        self.cfgBulider(node2)

        self.astBulider(parent, node1)
        self.astBulider(node1, node2) 

        bodySta = None
        bodySta = Statement(bodyNode, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = bodySta.handleConstructorBody()
        if cfg['nodes'] != []:
            self.lastNodeListAdd(bodySta._lastNode)
        else:
            self._lastNode.append(node2)
        # self.lastNodeListAdd(bodySta._lastNode)
        self.levelNodeListAdd(bodySta._levelNode)
        # self.continueLevelNodeListAdd(bodySta._continueLevelNode)
        # self.ifLevelNodeListAdd(bodySta._ifLevelNode)
        # self.throwLevelNodeListAdd(bodySta._throwNode)
        # self.yieldLevelNodeListAdd(bodySta._yieldNode)
        if statementNode != []:
            self._node.extend(statementNode)
        if ast['nodes'] != []:
            node3 = ast['nodes'][0]
            self.astBulider(parent, node3)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node4 = cfg['nodes'][0]
            self.cfgBulider(node2, node4)
            self.cfgJoint(cfg)

        return (self.getNodes(), self.getAst(), self.getCfg())
    
    def handleConstructorBody(self):
        '''
        constructor_body: $ => seq(
            '{',
            optional($.explicit_constructor_invocation),
            repeat($.statement),
            '}',
        ),
        '''
        parent = Node('constructor_body')

        
        node2 = None
        block = []
        lastChild = []
        for child in self._astNode.children:
            if child.type == 'explicit_constructor_invocation':
                node1 = Node('explicit_constructor_invocation')
                self.astBulider(parent, node1)
                # label = self._code[child.start_byte:child.end_byte]
                label = child.text.decode('utf-8')
                node2 = Node(label)
                self.astBulider(node1, node2)
            if child.type in self._statements:
                nSta = None
                # breakLevel = self._level
                # continueLevel = self._continueLevel
                # iflevel = self._ifLevel
                # # self._levelStatement is break level statement
                # if child.type in self._levelStatement:
                #     breakLevel = breakLevel + 1
                # if child.type in self._continueLevelStatement:
                #     continueLevel = continueLevel + 1
                # if child.type == 'if_statement':
                #     iflevel = iflevel + 1

                nSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                block.append((child, nSta))
                # fieldSta = Statement(child, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
                # statementNode, ast, cfg = fieldSta.handle()
                # self.lastNodeListAdd(fieldSta._lastNode)
                # self.levelNodeListAdd(fieldSta._levelNode)
                # # self.continueLevelNodeListAdd(fieldSta._continueLevelNode)
                # # self.ifLevelNodeListAdd(fieldSta._ifLevelNode)
                # # self.throwLevelNodeListAdd(fieldSta._throwNode)
                # # self.yieldLevelNodeListAdd(fieldSta._yieldNode)
                # if statementNode != []:
                #     self._node.extend(statementNode)
                # if ast['nodes'] != []:
                #     node3 = ast['nodes'][0]
                #     self.astBulider(parent, node3)
                #     self.astJoint(ast)
                # if cfg['nodes'] != []:
                #     node3 = cfg['nodes'][0]
                #     if node2 != None:
                #         self.cfgBulider(node2, node3)
                #     self.cfgJoint(cfg)
        
        caseBlockSta = Statement(None, self._code, self._level, self._ifLevel, self._continueLevel, self._tryLevel, self._yieldLevel)
        statementNode, ast, cfg = caseBlockSta.handleCaseBlock(block, parent)
        self.lastNodeListAdd(caseBlockSta._lastNode)
        self.levelNodeListAdd(caseBlockSta._levelNode)
        # self.continueLevelNodeListAdd(caseBlockSta._continueLevelNode)
        # self.ifLevelNodeListAdd(caseBlockSta._ifLevelNode)
        # self.throwLevelNodeListAdd(caseBlockSta._throwNode)
        # self.yieldLevelNodeListAdd(caseBlockSta._yieldNode)
        # lastChild.append((caseBlockSta))
        if statementNode != []:
            self._node.extend(statementNode)

        if ast['nodes'] != []:
            node14 = ast['nodes'][0]
            # self.astBulider(node11, node14)
            self.astJoint(ast)

        if cfg['nodes'] != []:
            node15 = cfg['nodes'][0]
            # if firstNode == None:
            #     firstNode = node15
            if node2 != None:
                self.cfgBulider(node2, node15)
            self.cfgJoint(cfg)
        return (self.getNodes(), self.getAst(), self.getCfg())