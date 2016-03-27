def const(x): return lambda _: x

def curry(f): return lambda x: lambda y: f(x,y)
