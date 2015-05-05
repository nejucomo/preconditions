from unittest import TestCase

from preconditions import PreconditionError, preconditions


class PreconditionTestBase (TestCase):
    def check_prec_fail(self, target, *args, **kw):
        self.assertRaises(PreconditionError, target, *args, **kw)


class InvalidPreconditionTests (PreconditionTestBase):
    def test_varargs(self):
        self.check_prec_fail(preconditions, lambda *a: True)

    def test_kwargs(self):
        self.check_prec_fail(preconditions, lambda **kw: True)

    def test_unknown_nondefault_param(self):
        # The preconditions refer to "x" but are applied to "a, b", so
        # "x" is unknown:
        p = preconditions(lambda x: True)

        self.check_prec_fail(p, lambda a, b: a+b)

    def test_default_masks_param(self):
        # Preconditions may have defaults as a hack to bind local
        # variables (such as when declared syntactically inside loops),
        # but this "closure hack" must not mask application function
        # parameter names:
        p = preconditions(lambda a, b='a stored value': True)

        self.check_prec_fail(p, lambda a, b: a+b)


class BasicPreconditionTests (PreconditionTestBase):
    def test_basic_precondition(self):

        @preconditions(lambda i: isinstance(i, int) and i > 0)
        def uint_pred(i):
            return i-1

        # Not greater than 0:
        self.check_prec_fail(uint_pred, 0)

        # Not an int:
        self.check_prec_fail(uint_pred, 1.0)

        # Test a successful call:
        self.assertEqual(0, uint_pred(1))

    def test_relational_precondition(self):

        @preconditions(lambda a, b: a < b)
        def inc_range(a, b):
            return range(a, b)

        self.check_prec_fail(inc_range, 3, 3)
        self.check_prec_fail(inc_range, 5, 3)

        self.assertEqual([3, 4], inc_range(3, 5))
