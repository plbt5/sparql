from pyparsing import ParseFatalException, ParseResults
from collections import OrderedDict
import sys

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')


# Conversion of EBNF syntax for SPARQL 1.1 to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#

class ParseInfo():
    def __init__(self, parseresults):
        assert isinstance(parseresults, ParseResults), type(parseresults)
        self.__dict__['name'] = parseresults.getName()
        self.__dict__['namedtokens'] = OrderedDict()
        self.__dict__['tokens'] = []
        valuedict = dict((id(v), k) for (k, v) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error'
        for t in parseresults:
            if isinstance(t, (str, SPARQLNode)):
                newtoken = [t]
            else:
                assert isinstance(t, ParseResults)
                newtoken = [ParseInfo(t)]
            self.__dict__['tokens'].append(newtoken)
            if id(t) in valuedict: 
                self.__dict__['namedtokens'][valuedict[id(t)]] = newtoken
                
    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.namedtokens.keys() != other.namedtokens.keys():
            return False
        for k in self.namedtokens.keys():
            if getattr(self, k) != getattr(other, k):
                return False
        if len(self.tokens) != len(other.tokens):
            return False
        for t1, t2 in zip(self.tokens, other.tokens):
            if t1 != t2:
                return False
        return True
    
    def __getattr__(self, name):
        assert name in self.namedtokens.keys()
        return self.namedtokens[name][0]
    
    def __setattr__(self, name, value):
        assert name in self.namedtokens
        assert type(self.__dict__['namedtokens'][name][0]) == type(value.parseinfo), 'assigned value must be of type {}, is of type {}'.format(type(self.namedtokens[name][0]), type(value)) 
        self.namedtokens[name][0] = value.parseinfo
        
    def getKeys(self):
        return self.namedtokens.keys()
    
    def getName(self):
        return self.name
    
    def render(self):
        reslist = []
        for t in map(lambda x: x[0], self.tokens):
            if isinstance(t, str):
                reslist.append(t) 
            else:
                assert isinstance(t, (SPARQLNode, ParseInfo))
                reslist.append(t.render())
        return ' '.join(reslist)


class SPARQLNode():
    
    def __init__(self, pr_or_str):
        self.assignPattern()
        if isinstance(pr_or_str, ParseResults):
            self.__dict__['parseinfo'] = ParseInfo(pr_or_str)
        else:
            assert isinstance(pr_or_str, str)
            newparseinfo = ParseInfo(self.pattern.parseString(pr_or_str))
            assert len(newparseinfo.tokens[0]) == 1
            self.__dict__['parseinfo'] = newparseinfo.tokens[0][0].parseinfo
            
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.pattern != other.pattern:
            return False
        return self.parseinfo == other.parseinfo
        
    def __repr__(self):
        return ' <<< Class:' + self.__class__.__name__ + ', dict=' + str(self.__dict__) + ' >>> '
    
    __str__ = __repr__
    
    def __getattr__(self, key):
        return getattr(self.parseinfo, key)
    
    def __setattr__(self, key, value):
        setattr(self.parsinfo, key, value)
        
    def getKeys(self):
        return self.parseinfo.getKeys()
    
    def render(self):
        return NotImplementedError

            
class Terminal(SPARQLNode):
    
    def render(self):
        return ''.join([t for t in map(lambda x: x[0], self.parseinfo.tokens)])
    __str__ = render
            
            
class NonTerminal(SPARQLNode):
    def render(self):
        return self.parseinfo.render()
    __str__ = render
    

def dumpSPARQLNode(node, indent=' ', depth=0):
    
    skip = indent * depth
    print(skip + '[' + node.__class__.__name__ + ']')
    if isinstance(node, Terminal):
        print(skip + str(node))
    else:
        assert isinstance(node, NonTerminal)
        dumpParseInfo(node.parseinfo, indent, depth + 1)


def dumpParseInfo(parseinfo, indent=' ', depth=0):
    skip = indent * depth
    for t in parseinfo.tokens:
        if isinstance(t[0], ParseInfo):
            name = t[0].getName()
            label = ('>> ' + name + ': ' if name else '')
            print(skip + label)
            dumpParseInfo(t[0], indent, depth+1)
        elif isinstance(t[0], str):
            print(skip + t[0])
        else:
            assert isinstance(t[0], SPARQLNode), type(t[0])
            dumpSPARQLNode(t[0], indent, depth)

 