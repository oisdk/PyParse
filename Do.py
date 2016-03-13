from functools import wraps

def do(monad):
    def do_wrapper(func):
        @wraps(func)
        def do_func(*args, **kwargs):
            def lazy():
                genr = func(*args, **kwargs)
                def send(x):
                    try: return genr.send(x).bind(send)
                    except StopIteration: return monad.pure(x)
                return send(None)
            return lazy
        return do_func
    return do_wrapper

