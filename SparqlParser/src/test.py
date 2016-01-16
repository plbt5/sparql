from collections import namedtuple
from pprint import pprint

c1 = namedtuple('c', 'name age')
c2 = namedtuple('c', 'name age city')

c3 = namedtuple('d', 'f1 f2')

print(dir(c1))
print(dir(c2))

t1 = c1(name='jan', age=31)
t2 = c2(name='piet', age=57, city='Amsterdam')

t3 = c3(f1=t1, f2=t2)

# print(type(c1))
# print(type(c2))
# print(t1, type(t1), t1._fields)
# print(t2, type(t2), t2._fields)
# print(t3, type(t3), t3._fields)

print(t3._asdict())

print()


def print_namedtuple(t, depth=0):
    for k in t._fields:
        print(' '*depth + k, end=':')
        v = getattr(t, k)
        if isinstance(v, tuple):
            print()
            print_namedtuple(v, depth+1)
        else:
            print(v)
            
            

print_namedtuple(t3)