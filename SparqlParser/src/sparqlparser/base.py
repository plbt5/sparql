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
    
    def __init__(self, *args):
        self.assignPattern()
        if len(args) == 2:
            self.__dict__['name'] = args[0] # name
            self.__dict__['items'] = args[1] # items
        else:
            assert len(args) == 1 and isinstance(args[0], str)
            self.__dict__['name'] = None
            self.__dict__['items'] = self.pattern.parseString(args[0])[0].items
                
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
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
    def __setattr__(self, name, value):
        assert name in self.getKeys()
        items = self.getItemsForKey(name)
        assert len(items) == 1
        assert type(items[0][1] == type(value)), 'assigned value must be of type {}, is of type {}'.format(type(items[0][1]), type(value)) 
        self.items[0][1] = value
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
    
    def getItemsForKey(self, k):
        result = [i for i in self.getItems() if i[0] == k]
        if len(result) > 1:
            raise NotImplementedError('Multiple items ({}) for key {} not yet supported'.format(result, k))
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



class SPARQLElement(ParseInfo):
    pass


class SPARQLNode(SPARQLElement):
    pass

            
class SPARQLTerminal(SPARQLNode):
    def render(self):
        return ''.join([t[1] for t in self.items])
    __str__ = render
            
            
class SPARQLNonTerminal(SPARQLNode):
    pass


class SPARQLKeyword(SPARQLElement):
    pass
    




 