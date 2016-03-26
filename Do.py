from functools import wraps

def do(monad):
    """An implementation of Haskell's do-notation, using generators.
    Do-notation in Haskell looks like this:
        m = do
          x <- a
          y <- b
          pure (x, y)
    This implementation in Python looks like this:
        @do(Monad)
        def m():
            x = yield a
            y = yield b
            Monad.pure((x,y))
    Where `Monad` corresponds to the particular monad being used.
    """
    def do_wrapper(func):
        @wraps(func)
        def do_func(*args, **kwargs):
            def lazy():
                genr = func(*args, **kwargs)
                def send(x):
                    try: return genr.send(x).bind(send)
                    except StopIteration: return monad.pure(x)
                return send(None)
            return lazy if args or kwargs else lazy()
        return do_func
    return do_wrapper

