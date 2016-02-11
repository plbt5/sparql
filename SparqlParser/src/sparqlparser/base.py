from pyparsing import ParseFatalException, ParseException
import sys

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')


# Conversion of EBNF syntax for SPARQL 1.1 to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#


class ParseInfo():
    
    def __init__(self, *args):
        self.__dict__['pattern'] = self.assignPattern()
        if len(args) == 2:
            self.__dict__['name'] = args[0] 
            self.__dict__['items'] = args[1] 
        else:
            assert len(args) == 1 and isinstance(args[0], str)
            self.__dict__['name'] = None
            self.__dict__['items'] = self.pattern.parseString(args[0], parseAll=True)[0].items
        assert self.__isKeyConsistent()
                
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name and self.items == other.items
    
    def __getattr__(self, key):
        if key in self.getKeys():
            values = self.getValuesForKey(key)
            assert len(values) == 1
            return values[0] 
        else:
            raise AttributeError('Unknown key: {}'.format(key))
#     
    def __setattr__(self, key, value):
        if key in self.getKeys():
            items = self.getItemsForKey(key)
            assert len(items) == 1
            assert items[0][0] == key
            oldtype = type(items[0][1])
            value.__dict__['name'] = items[0][0]
            items[0][1] = value     
            assert self.__isKeyConsistent()               
        else:
            raise AttributeError('Unknown key: {}'.format(key))
   
    def __isKeyConsistent(self):
        return all([t[0] == t[1].name if isinstance(t[1], ParseInfo) else t[0] == None if isinstance(t[1], str) else False for t in self.getItems()])
    
    def assignPattern(self):
        raise NotImplementedError

    def getName(self):
        return self.name
    
    def getItems(self):
        return self.items
    
    def getValues(self):
        return [i[1] for i in self.getItems()]
    
    def getKeys(self):
        return [i[0] for i in self.getItems() if i[0]]
    
    def hasKey(self, k):
        return k in self.getKeys()
    
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
            for _, v in items:
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
    
    def yieldsValidExpression(self):
        try:
            self.pattern.parseString(self.render(), parseAll=True)
            return True
        except ParseException:
            return False
        
    def isValid(self):
        return self == self.pattern.parseString(self.render())[0]



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
    




 