class PreconditionError (TypeError):
    pass


def preconditions(*precs):
    def decorate(f):
        def g(*a, **kw):
            return f(*a, **kw)
        return g
    return decorate
