from functools import wraps
import inspect


class PreconditionError (TypeError):
    pass


def preconditions(*precs):
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
                'Precondition {!r} must not accept * nor ** args.'.format(p))

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
                        ('Precondition {!r} specifies non-default arg {!r}' +
                         ' which is not one of the known application args:' +
                         ' {!s}')
                        .format(p, apparg, ', '.join(fspec.args)))
            for carg in closureargs:
                if carg in fspec.args:
                    raise PreconditionError(
                        ('Precondition {!r} specifies default arg {!r}' +
                         ' which masks one of the known application args:' +
                         ' {!s}')
                        .format(p, carg, ', '.join(fspec.args)))

        @wraps(f)
        def g(*a, **kw):
            args = inspect.getcallargs(f, *a, **kw)
            for (appargs, _, p) in precinfo:
                if not p(*[args[aa] for aa in appargs]):
                    raise PreconditionError(
                        'Precondition {!r} failed in call: {!r}{}'
                        .format(
                            p,
                            g,
                            inspect.formatargvalues(
                                fspec.args,
                                fspec.varargs,
                                fspec.keywords,
                                args)))

            return f(*a, **kw)

        g.nopre = f
        return g
    return decorate
