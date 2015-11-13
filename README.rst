============
 oscar.flag
============

.. begin

``oscar.flag`` provides extensible, namespaced flags which can be
parsed from environment variables, command-line arguments and config
files.

Flags are declared where they are used in an application or library,
and they are accessed through a namespace matching their fully
qualified module path.

Documentation lives at `Read the Docs
<https://oscarflag.readthedocs.org/>`_, the code on `GitHub
<https://github.com/oscarhealth/oscar.flag>`_.

Example
=======

Application entry-point::

   import sys
   from oscar import flag

   import other_module


   FLAGS = flag.namespace(__name__)
   FLAGS.some_int = flag.Int('some integer value', default=1)


   if __name__ == '__main__':
       flag.parse_commandline(sys.argv[1:])
       flag.die_on_missing_required()

       print 'other_module.multiply_by(%d) = %d' % (
           FLAGS.some_int,
           other_module.multiply_by(FLAGS.some_int))

other_module.py::

   from oscar import flag

   FLAGS = flag.namespace(__name__)
   FLAGS.multiplier = flag.Int('some integer', default=flag.REQUIRED)

   def multiply_by(i):
       return i * FLAGS.multiplier

shell::

   $ python example.py
   Missing required flags:
   	 [other_module.]multiplier
   Usage of example.py:
   __main__:
   	 [__main__.]some_int=None: some integer value

   other_module:
   	 [other_module.]multiplier=<required>: some integer

   # Note the namespaced reference --other_module.multiplier.
   $ python example.py --other_module.multiplier=2 --some_int=3
   other_module.multiply_by(3) = 6

License
=======

Copyright 2015 Mulberry Health Inc.

Licensed under the `Apache License, Version
2.0. <http://www.apache.org/licenses/LICENSE-2.0>`_
