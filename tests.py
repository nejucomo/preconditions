from unittest import TestCase

from preconditions import PreconditionError, preconditions


class InvalidPreconditionTests (TestCase):
    def test_varargs(self):
        self.assertRaises(PreconditionError, preconditions, lambda *a: True)

    def test_kwargs(self):
        self.assertRaises(PreconditionError, preconditions, lambda **kw: True)

    def test_unknown_nondefault_param(self):
        # The preconditions refer to "x" but are applied to "a, b", so
        # "x" is unknown:
        p = preconditions(lambda x: True)

        self.assertRaises(PreconditionError, p, lambda a, b: a+b)

    def test_default_masks_param(self):
        # Preconditions may have defaults as a hack to bind local
        # variables (such as when declared syntactically inside loops),
        # but this "closure hack" must not mask application function
        # parameter names:
        p = preconditions(lambda a, b='a stored value': True)

        self.assertRaises(PreconditionError, p, lambda a, b: a+b)


class BasicPreconditionTests (TestCase):
    def test_basic_precondition(self):

        @preconditions(lambda i: isinstance(i, int) and i > 0)
        def uint_pred(i):
            return i-1

        # Not greater than 0:
        self.assertRaises(PreconditionError, uint_pred, 0)

        # Not an int:
        self.assertRaises(PreconditionError, uint_pred, 1.0)

        # Test a successful call:
        self.assertEqual(0, uint_pred(1))

    def test_relational_precondition(self):

        @preconditions(lambda a, b: a < b)
        def inc_range(a, b):
            return range(a, b)

        self.assertRaises(PreconditionError, inc_range, 3, 3)
        self.assertRaises(PreconditionError, inc_range, 5, 3)

        self.assertEqual([3, 4], inc_range(3, 5))
