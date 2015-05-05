import inspect


class PreconditionError (TypeError):
    pass


def preconditions(*precs):

    precinfo = []
    for p in precs:
        spec = inspect.getargspec(p)
        if spec.varargs or spec.keywords:
            raise PreconditionError(
                'Precondition {!r} must not accept * nor ** args.'.format(p))

        i = -len(spec.defaults)
        appargs, closureargs = spec.args[:i], spec.args[i:]
        precinfo.append( (appargs, closureargs, p) )

    def decorate(f):
        def g(*a, **kw):
            return f(*a, **kw)
        return g
    return decorate
