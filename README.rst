=============
preconditions
=============

``preconditions`` - A precondition decorator utility which relies on
`parameter-name equivalence` for conciseness and consistency.

Examples
========

First let's take a tour of examples. All examples assume the
``preconditions`` decorator has been imported:

.. code:: python

   from preconditions import preconditions

Basic type checking
-------------------

The ``double`` function requires, as a precondition, that the ``i``
parameter is an ``int``:

.. code:: python

   @preconditions(lambda i: isinstance(i, int))
   def double(i):
       return 2*i

Multiple predicates
-------------------

Multiple predicates may be specified:

.. code:: python

   @preconditions(
       lambda i: isinstance(i, int),
       lambda i: i > 0,
       )
   def double(i):
       return 2*i

Note that this is functionally equivalent to this single predicate
version:

.. code:: python

   @preconditions(
       lambda i: isinstance(i, int) and i > 0,
       )
   def double(i):
       return 2*i

The multi-predicate version should (eventually) have more specific
error reporting for a failure, while the single predicate version may
be more efficient.

Multiple arguments
------------------

Multiple predicates can express preconditions for multiple arguments:

.. code:: python

   @preconditions(
       lambda s: isinstance(s, unicode),
       lambda n: isinstance(n, int) and n >= 0,
       )
   def repeat(s, n):
       return s*n

However, a *single predicate* can express preconditions for multiple
arguments. This allows `relational preconditions`:

.. code:: python

   @preconditions(
       lambda a, b: a <= b
       )
   def strict_range(a, b):
       return range(a, b)

Method preconditions
--------------------

Predicates can be expressed for methods, including relations to
``self``. For example, a ``Monotonic`` instance ensures that each call to
``.set`` must pass a value larger than any previous call:

.. code:: python

   class Monotonic (object):
       def __init__(self):
           self.v = 0

       @preconditions(lambda self, v: v > self.v)
       def set(self, v):
           self.v = v

Preconditions can be applied to special methods, such as ``__new__``,
``__init__``, ``__call__``, etc...

.. code:: python

   class LinearRange (tuple):
       @preconditions(
              lambda a: isinstance(a, float),
              lambda b: isinstance(b, float),
              lambda a, b: a < b,
              )
       def __new__(cls, a, b):
           return super(OrderedTuple, cls).__new__(cls, (a, b))

       @preconditions(lambda w: 0 <= w < 1.0)
       def __call__(self, w):
           lo, hi = self
           return w * (hi - lo) + lo

       @preconditions(lambda x: self[0] <= x < self[1])
       def invert(self, x):
           lo, hi = self
           return (x - lo) / (hi - lo)

Concepts
========

An `application function` may be guarded with `precondition
predicates`. These `predicates` are callables passed to the
``preconditions`` decorator. Consider this code:

.. code:: python

   @preconditions(
       lambda a: isinstance(a, float) and a >= 0,
       lambda b: isinstance(b, float) and b >= 0,
       )
   def area(a, b):
       return a*b

The application function is ``area``, and it has two predicates defined
with ``lambda``, each of which ensures one of the arguments is a
non-negative float.

Parameter Name Equivalence
--------------------------

The parameter names in a predicate must match parameter names in
the application function. This is known as `parameter name equivalence`
[#]_.

.. [#] This is a bit magical, relying on function introspection. The
       design assumes the conciseness and consistency benefits outweigh
       the potential confusion of "magic".

One exception to this rule is for default parameters within
predicates. Default parameters may be used to associate some state at
predicate definition time. For example:

.. code:: python

   scores = {}

   @preconditions(
       lambda color, _colors=['RED', 'GREEN', 'BLUE']: color in _colors
       )
   def get_color_score(color):
       return scores[color]

This feature may be most convenient when there's a need to remember a
local loop variable.

.. FIXME: create an example.

