from unittest import TestCase, main

from preconditions import PreconditionError, preconditions


class PreconditionTestBase (TestCase):
    def assertPreconditionFails(self, target, *args, **kw):
        self.assertRaises(PreconditionError, target, *args, **kw)

    def assertPreconditionFailsRegexp(self, rgx, target, *args, **kw):
        self.assertRaisesRegexp(PreconditionError, rgx, target, *args, **kw)


class InvalidPreconditionTests (PreconditionTestBase):
    def test_varargs(self):
        self.assertPreconditionFailsRegexp(
            (r'^Invalid precondition must not accept \* nor \*\* args:\n' +
             r'  lambda \*a: True,\n$'),
            preconditions,
            lambda *a: True,
            )

    def test_kwargs(self):
        self.assertPreconditionFailsRegexp(
            (r'^Invalid precondition must not accept \* nor \*\* args:\n' +
             r'  lambda \*\*kw: True,\n$'),
            preconditions,
            lambda **kw: True,
            )

    def test_unknown_nondefault_param(self):
        p = preconditions(lambda x: True)

        self.assertPreconditionFailsRegexp(
            (r"^Invalid precondition refers to unknown parameter 'x':\n" +
             r"  p = preconditions\(lambda x: True\)\n" +
             r"Known parameters: \['a', 'b'\]\n$"),
            p,
            lambda a, b: a+b)

    def test_default_masks_param(self):
        p = preconditions(lambda a, b='a stored value': True)

        self.assertPreconditionFailsRegexp(
            (r"^Invalid precondition masks parameter 'b':\n" +
             r"  p = preconditions\(lambda a, b='a stored value': True\)\n" +
             r"Known parameters: \['a', 'b'\]\n$"),
            p,
            lambda a, b: a+b)


class BasicPreconditionTests (PreconditionTestBase):
    def test_basic_precondition(self):

        @preconditions(lambda i: isinstance(i, int) and i > 0)
        def uint_pred(i):
            return i-1

        # Not greater than 0:
        self.assertPreconditionFails(uint_pred, 0)

        # Not an int:
        self.assertPreconditionFails(uint_pred, 1.0)

        # Test a successful call:
        self.assertEqual(0, uint_pred(1))

    def test_relational_precondition(self):

        @preconditions(lambda a, b: a < b)
        def inc_range(a, b):
            return range(a, b)

        self.assertPreconditionFails(inc_range, 3, 3)
        self.assertPreconditionFails(inc_range, 5, 3)

        self.assertEqual([3, 4], inc_range(3, 5))

    def test_multiple_preconditions(self):

        @preconditions(
            lambda a: isinstance(a, float),
            lambda b: isinstance(b, int),
            lambda b: b > 0,
            lambda a, b: a < b,
            )
        def f(a, b):
            return a ** b

        self.assertPreconditionFails(f, 3, 5)
        self.assertPreconditionFails(f, 3.0, 5.0)
        self.assertPreconditionFails(f, 3.0, -2)
        self.assertPreconditionFails(f, 3.0, 2)

        self.assertEqual(0.25, f(0.5, 2))

    def test_zero_preconditions(self):
        p = preconditions()

        def f():
            return None

        g = p(f)

        self.assertIs(None, f())
        self.assertIs(None, g())
        self.assertIs(f, g)

    def test_precondition_with_default(self):

        @preconditions(lambda a, _s=[2, 3, 5]: a in _s)
        def f(a):
            return a

        self.assertPreconditionFails(f, 4)
        self.assertEqual(3, f(3))


class MethodPreconditionTests (PreconditionTestBase):
    def test_invariant_precondition(self):

        class C (object):
            @preconditions(lambda self: self.key in self.items)
            def get(self):
                return self.items[self.key]

        i = C()
        i.items = {'a': 'apple', 'b': 'banana'}
        i.key = 'X'

        self.assertPreconditionFails(i.get)

        i.key = 'b'

        self.assertEqual('banana', i.get())

    def test__init__(self):

        class C (object):
            @preconditions(lambda name: isinstance(name, unicode))
            def __init__(self, name):
                self.name = name

        self.assertPreconditionFails(C, b'Not unicode!')
        self.assertEqual(u'Alice', C(u'Alice').name)

    def test_old_school__init__(self):

        class C:
            @preconditions(lambda name: isinstance(name, unicode))
            def __init__(self, name):
                self.name = name

        self.assertPreconditionFails(C, b'Not unicode!')
        self.assertEqual(u'Alice', C(u'Alice').name)

    def test__new__(self):

        class C (tuple):
            @preconditions(lambda a, b: a < b)
            def __new__(self, a, b):
                return tuple.__new__(self, (a, b))

        self.assertPreconditionFails(C, 5, 3)
        self.assertEqual((3, 5), C(3, 5))

    def test_old_school_method(self):

        class OldSchool:
            def __init__(self, x):
                self.x = x

            @preconditions(lambda self, x: self.x < x)
            def increase_to(self, x):
                self.x = x

        obj = OldSchool(5)

        self.assertPreconditionFails(obj.increase_to, 3)

        obj.increase_to(7)

        self.assertPreconditionFails(obj.increase_to, 6)


class PreconditionInterfaceTests (PreconditionTestBase):
    def test__name__(self):
        @preconditions(lambda x: True)
        def f(x):
            return x

        self.assertEqual('f', f.__name__)

    def test_zero_preconditions__name__(self):
        @preconditions()
        def f(x):
            return x

        self.assertEqual('f', f.__name__)

    def test_nopre(self):
        def assert_false():
            assert False

        p = preconditions(lambda x: assert_false())

        def f(x):
            return 2*x

        g = p(f)

        self.assertIs(f, g.nopre)
        self.assertEqual(6, g.nopre(3))

    def test_zero_preconditions_nopre(self):
        p = preconditions()

        def f(x):
            return 2*x

        g = p(f)

        self.assertIs(f, g.nopre)
        self.assertEqual(6, g.nopre(3))


class ErrorReportingTests (PreconditionTestBase):
    def test_single_predicate_single_line_failure_includes_source(self):
        @preconditions(lambda x: x != 7)
        def f(x):
            return x

        self.assertPreconditionFailsRegexp(
            (r'^Precondition failed in call ' +
             r'<function f at 0x[0-9a-fA-F]+>\(x=7\):\n' +
             r'  @preconditions\(lambda x: x != 7\)\n$'),
            f,
            7)

    def test_multiple_line_multiple_predicates_includes_specific_source(self):
        @preconditions(
            lambda x: x > 0,
            lambda x: isinstance(x, int),
            )
        def f(x):
            return x

        self.assertPreconditionFailsRegexp(
            (r'Precondition failed in call ' +
             r'<function f at 0x[0-9a-fA-F]+>\(x=6\.5\):\n' +
             r'  lambda x: isinstance\(x, int\),\n$'),
            f,
            6.5)



if __name__ == '__main__':
    main()
