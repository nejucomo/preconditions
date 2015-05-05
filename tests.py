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
