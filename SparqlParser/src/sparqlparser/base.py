from pyparsing import ParseFatalException, ParseResults
from collections import OrderedDict
import sys
from _operator import itemgetter

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')


# Conversion of EBNF syntax for SPARQL 1.1 to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#



class ParseInfo():
    
    def __init__(self, name, items):
        self.__dict__['name'] = name
        self.__dict__['items'] = items
        self.assignPattern()
                
    def __eq__(self, other):
        if self.name != other.name:
            return False
        for t1, t2 in zip(self.items, other.items):
            if t1 != t2:
                return False
        return True
    
    def __getattr__(self, name):
        values = self.getValuesForKey(name)
        assert len(values) == 1, len(values)
        return values[0]
#     
#     def __setattr__(self, name, value):
#         assert name in self.namedtokens
#         assert type(self.__dict__['namedtokens'][name][0]) == type(value.parseinfo), 'assigned value must be of type {}, is of type {}'.format(type(self.namedtokens[name][0]), type(value)) 
#         self.namedtokens[name][0] = value.parseinfo
#         
    def assignPattern(self):
        pass

    def getName(self):
        return self.name
    
    def getItems(self):
        return self.items
    
    def getValues(self):
        return [i[1] for i in self.getItems()]
    
    def getKeys(self):
        return [i[0] for i in self.getItems() if i[0]]
    
    def getValuesForKey(self, k):
        result = [i[1] for i in self.getItems() if i[0] == k]
        if len(result) > 1:
            raise NotImplementedError('Multiple values ({}) for key {} not yet supported'.format(result, k))
        return result
    
    


    def dump(self, indent='', step='  '):
        
        def dumpString(s, indent, step):
            print(indent + '- ' + s + ' <str>' )
        
        def dumpItems(items, indent, step):
            for k, v in items:
                if isinstance(v, str):
                    dumpString(v, indent+step, step)
                elif isinstance(v, list):
                    dumpItems(v, indent+step, step)
                else:
                    assert isinstance(v, ParseInfo)
                    v.dump(indent+step, step)       
       
        print(indent + ('> '+ self.name + ':\n' + indent if self.name else '') + '[' + self.__class__.__name__ + '] ' + self.render())
        dumpItems(self.items, indent, step)
    


    def render(self):
        sep = ' '
        def renderList(l):
            resultList = []
            for i in l:
                if isinstance(i, str):
                    resultList.append(i)
                    continue
                if isinstance(i, ParseInfo):
                    resultList.append(i.render())
                    continue
                if isinstance(i, list):
                    resultList.append(renderList(i))
            return sep.join(resultList)
        result = []
        for t in self.items:
            if isinstance(t[1], str):
                result.append(t[1]) 
            elif isinstance(t[1], list):
#                 result.append(t.renderItems(sep))
                result.append(renderList(t[1]))
            else:
                assert isinstance(t[1], ParseInfo), type(t[1])
                result.append(t[1].render())
        return sep.join(result)

#     def render(self, sep=' '):
#         return self.renderItems(sep)

    

class SPARQLNode(ParseInfo):
    pass

            
class Terminal(SPARQLNode):
    def render(self):
        return ''.join([t[1] for t in self.items])
    __str__ = render
            
            
class NonTerminal(SPARQLNode):
    pass

class SPARQLKeyword(ParseInfo):
    pass
    

# def dumpSPARQLNode(node, indent='  ', depth=0):
#     
#     skip = indent * depth
#     print(skip + '[' + node.__class__.__name__ + ']')
#     if isinstance(node, Terminal):
#         print(skip + str(node))
#     else:
#         assert isinstance(node, NonTerminal)
#         dumpParseInfo(node.parseinfo, indent, depth + 1)


# def dumpParseInfo(parseinfo, indent='  ', depth=0):
#     skip = indent * depth
#     
#     if isinstance(parseinfo, SPARQLNode):
#         clsName = '[' + parseinfo.__class__.__name__ + ']'
#     else:
#         clsName = '[ParseInfo]'
#     print(skip + clsName)
# 
#     for t in parseinfo.tokens:
#         if isinstance(t, ParseInfo):
#             name = t.getName()
#             if name == None:
#                 label = indent + '(no name)'
#             elif name == 'group':
#                 label = indent + '(group)'
#             else:
#                 label = (indent + '<key> "' + name + '"')
#             print(skip + label)
#             dumpParseInfo(t, indent, depth+1)
#         elif isinstance(t, ParseResults):
#             dumpParseInfo(ParseInfo(t), indent, depth+1)
#         else:
#             assert isinstance(t, str)
#             print(skip + indent + '<str> ' + t)



 