from functools import wraps
import inspect


class PreconditionError (TypeError):
    pass


def preconditions(*precs):
    stripped_source = lambda obj: inspect.getsource(obj).strip()

    if not precs:
        # This edge case makes ``@preconditions()`` efficiently delegate
        # to the wrapped function, which I anticipate will be useful
        # for stubbing and code consistency in applications:
        def null_decorator(f):
            f.nopre = f # Meet the .nopre interface requirement.
            return f
        return null_decorator

    precinfo = []
    for p in precs:
        spec = inspect.getargspec(p)
        if spec.varargs or spec.keywords:
            raise PreconditionError(
                ('Invalid precondition must not accept * nor ** args:\n' +
                 '  {!s}\n')
                .format(stripped_source(p)))

        i = -len(spec.defaults or ())
        if i == 0:
            appargs, closureargs = spec.args, []
        else:
            appargs, closureargs = spec.args[:i], spec.args[i:]
        precinfo.append( (appargs, closureargs, p) )

    def decorate(f):
        fspec = inspect.getargspec(f)

        for (appargs, closureargs, p) in precinfo:
            for apparg in appargs:
                if apparg not in fspec.args:
                    raise PreconditionError(
                        ('Invalid precondition refers to unknown parameter {!r}:\n' +
                         '  {!s}\n' +
                         'Known parameters: {!r}\n')
                        .format(
                            apparg,
                            stripped_source(p),
                            fspec.args))
            for carg in closureargs:
                if carg in fspec.args:
                    raise PreconditionError(
                        ('Invalid precondition masks parameter {!r}:\n' +
                         '  {!s}\n' +
                         'Known parameters: {!r}\n')
                        .format(
                            carg,
                            stripped_source(p),
                            fspec.args))

        @wraps(f)
        def g(*a, **kw):
            args = inspect.getcallargs(f, *a, **kw)
            for (appargs, _, p) in precinfo:
                if not p(*[args[aa] for aa in appargs]):
                    raise PreconditionError(
                        'Precondition failed in call {!r}{}:\n  {!s}\n'
                        .format(
                            g,
                            inspect.formatargvalues(
                                fspec.args,
                                fspec.varargs,
                                fspec.keywords,
                                args),
                            stripped_source(p)))

            return f(*a, **kw)

        g.nopre = f
        return g
    return decorate
