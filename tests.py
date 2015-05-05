from unittest import TestCase

from preconditions import PreconditionError, preconditions


class InvalidPreconditionTests (TestCase):
    def test_varargs_in_precondition(self):
        self.assertRaises(PreconditionError, preconditions, lambda *a: a)
