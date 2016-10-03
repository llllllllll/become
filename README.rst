``become``
==========

Make one object become another.

Example
-------

.. code-block:: python

   In [1]: class C:
      ...:     pass
      ...:

   In [2]: class D:
      ...:     pass
      ...:

   In [3]: c = C()

   In [4]: d = D()

   In [5]: tup = c, d

   In [6]: ls = [c, d]

   In [7]: from become import become

   In [8]: become(c, d)  # returns the number of places where c existed
   Out[8]: 10

   In [9]: c
   Out[9]: <__main__.D at 0x7f5b04285be0>

   In [10]: d
   Out[10]: <__main__.D at 0x7f5b04285be0>

   In [11]: c is d
   Out[11]: True

   In [12]: tup
   Out[12]: (<__main__.D at 0x7f5b04285be0>, <__main__.D at 0x7f5b04285be0>)

   In [13]: ls
   Out[13]: [<__main__.D at 0x7f5b04285be0>, <__main__.D at 0x7f5b04285be0>]

   In [14]: tup[0] is tup[1] is ls[0] is ls[1] is d is c
   Out[14]: True

Dependencies
------------

``become`` only works on Python 3.

Oh, and it also requires CPython, C++14, `libpy
<https://github.com/llllllllll/libpy>`_, Linux (the kernel), and x86_64.

We recommend using ``gcc`` to compile ``become`` and ``libpy``.
