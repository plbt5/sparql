import io
test = io.StringIO()

test.write('hello')

s = test.getvalue()

print(s, type(s))

s = test.getvalue()

print(s, type(s))

test.write('world')

print(test.getvalue())

print('hereiam', file=test)

print(test.getvalue())
