from functools import reduce, partial, wraps

def const(x): return lambda _: x

def curry(f): return lambda x: lambda y: f(x,y)

def compose(*f): return reduce(lambda g,f: lambda x: g(f(x)), f)

def tco(func):
    @wraps(func)
    def func_run(*args, **kwargs):
        res = func(*args, **kwargs)
        while type(res) == tuple and len(res) == 2 and callable(res[0]):
            fun, val = res
            try: fun = getattr(fun, 'tco_rec')
            except AttributeError:
                return fun(*val) if type(val) == tuple else fun(val)
            res = fun(*val) if type(val) == tuple else fun(val)
        return res
    func_run.tco_rec = func
    return func_run

@tco
def upTo(n, i=0):
    print(i)
    if i >= n: return i
    else: return upTo, (n, i+1)

def upToNoTCO(n, i=0):
    print(i)
    if i >= n: return i
    else: return upToNoTCO(n, i+1)

@tco
def even(n):
    return n == 0 or n != 1 and (odd, n-1)

@tco
def odd(n):
    return n == 1 or n != 0 and (even, n-1)

from random import randrange, choice

def randbracks(size, ops):
    l, r = ('(', ')') if randrange(2) else (' ', ' ')
    if size <= 1:
        contents = yield l
        yield str(contents)
    else:
        yield l
        for i in range(randrange(1, size)):
            if i: yield ' ' + choice(ops) + ' '
            yield from randbracks(size // 2, ops)
    yield r

def randnums(len):
    genr = randbracks(len, ['+', '-', '*'])
    yield genr.send(None)
    while True:
        try: yield genr.send(randrange(100) - 50)
        except StopIteration: break

def randbools(len):
    genr = randbracks(len, ['and', 'or'])
    yield genr.send(None)
    while True:
        try: yield genr.send(bool(randrange(2)))
        except StopIteration: break

