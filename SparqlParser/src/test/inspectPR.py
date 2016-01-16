from pyparsing import *

def inspect(pr): # ParseResults
    if not isinstance(pr, ParseResults):
        raise Exception('Expected ParseResults, got {}'.format(pr.__class__.__name__))
#     print('repr: {}', repr(pr))
#     print('items: {}'.format([item for item in pr.items()]))
    print('as list: {}\n'.format(pr.asList()))
#     print('as dict: {}'.format(pr.asDict()))
#     print('name: {}'.format(pr.getName()))
    print('dump: {}\n'.format(pr.dump()))
    
L = Word('[a-z]')
U = Word('[A-Z]')
A = L ^ U

# inspect(( L('item1') + U('item2')).parseString('aaa ZZZ'))
# print()
# inspect(A.parseString('aaa ZZZ'))
# print()



L.setParseAction(lambda x: 'foo' + str(x.tokens))
U.setParseAction(lambda x: 'bar' + str(x.tokens))
A.setParseAction(lambda x: 'spam' + str(x.tokens))
 
inspect(( L('item1') + U('item2')).parseString('aaa ZZZ'))
print()
inspect( (L('item1') | U('item2')).parseString('aaa ZZZ'))
print()
inspect( (A('item3')).parseString('aaa ZZZ'))
print()