from pyparsing import ParseFatalException, ParseResults
import sys

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling issues)')


# Conversion of EBNF syntax for SPARQL 1.1 to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#

class SPARQLNode():
    
    def __init__(self, pr):
        self.assignPattern()
        if isinstance(pr, ParseResults):
            self.pr = pr
        else:
            assert isinstance(pr, str)
            self.pr = self.pattern.parseString(pr)[0].pr
    def __getattr__(self, k):
        return getattr(self.pr, k)
    def keys(self):
        return self.pr.keys()
    def __repr__(self):
        return ' <<< Class:' + self.__class__.__name__ + ', dict=' + str(self.__dict__) + ' >>> '
    __str__ = __repr__

    
            
class Terminal(SPARQLNode):
    
    def __str__(self):
        return ''.join([t for t in self.pr])
            
            
class NonTerminal(SPARQLNode):
    pass
            

def dumpSPARQLNode(node, indent=' ', depth=0):
    
    skip = indent * depth
    print(skip + '[' + node.__class__.__name__ + ']')
    if isinstance(node, Terminal):
        print(skip + str(node))
    else:
        assert isinstance(node, NonTerminal)
        dumpParseResults(node.pr, indent, depth + 1)


def dumpParseResults(pr, indent=' ', depth=0):
    skip = indent * depth
    for t in pr:
        if isinstance(t, ParseResults):
            try:
                label = ('>> ' + t.getName() + ': ' if t.getName() else '')
            except AttributeError:
                label = ''
            print(skip + label)
            dumpParseResults(t, indent, depth+1)
        elif isinstance(t, str):
            print(skip + t)
        else:
            assert isinstance(t, SPARQLNode)
            dumpSPARQLNode(t, indent, depth)
            
def dumpElement(pr, indent=' ', depth=0):
    if isinstance(pr, ParseResults):
        dumpParseResults(pr, indent, depth)
    else:
        assert isinstance(pr, SPARQLNode)
        dumpSPARQLNode(pr, indent, depth)
            
            
def renderSPARQLNode(node):
    if isinstance(node, Terminal):
        return str(node)
    else:
        assert isinstance(node, NonTerminal)
        return renderParseResults(node.pr)
     
     
def renderParseResults(pr):
    reslist = []
    for t in pr:
        if isinstance(t, str):
            reslist.append(t) 
        elif isinstance(t, SPARQLNode):
            reslist.append(renderSPARQLNode(t))
        else:
            assert isinstance(t, ParseResults)
            reslist.append(renderParseResults(t))
    return ' '.join(reslist)