from functools import reduce, partial

def const(x): return lambda _: x

def curry(f): return lambda x: lambda y: f(x,y)

def compose(*f): return reduce(lambda g,f: lambda x: g(f(x)), f)
