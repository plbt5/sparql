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
        self.name = parseresults.getName()
        self.dict = OrderedDict()
        self.tokens = []
        valuedict = dict((id(v), k) for (k, v) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error'
        for t in parseresults:
            if isinstance(t, (str, SPARQLNode)):
                newtoken = [t]
            else:
                assert isinstance(t, ParseResults)
                newtoken = [ParseInfo(t)]
            self.tokens.append(newtoken)
            if id(t) in valuedict: 
                self.dict[valuedict[id(t)]] = newtoken
    def __getattr__(self, key):
        return self.dict[key][0]
    def getKeys(self):
        return self.dict.keys()
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
    
    def __init__(self, pr):
        self.assignPattern()
        if isinstance(pr, ParseResults):
            self.parseinfo = ParseInfo(pr)
        else:
            assert isinstance(pr, str)
            self.parseinfo = ParseInfo(self.pattern.parseString(pr))
    def __repr__(self):
        return ' <<< Class:' + self.__class__.__name__ + ', dict=' + str(self.__dict__) + ' >>> '
    __str__ = __repr__
    def __getattr__(self, key):
        return getattr(self.parseinfo, key)
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

 