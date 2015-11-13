=======
 Usage
=======

.. currentmodule:: oscar.flag

Declaring Flags
===============

Many constant values should be declared as flags. Obtained a
:py:class:`NamespaceFlagSet` from the :py:const:`GLOBAL_FLAGS`
singleton :py:class:`GlobalFlagSet` object via the
:py:func:`namespace` function.

.. code-block:: python
   :caption: Create namespaced ``FLAGS`` object.
   
   from oscar import flag
   
   FLAGS = flag.namespace(__name__)

There should not be a need to create a :py:class:`GlobalFlagSet` object manually
in typical usage.  Flag primitives predefined in the flag module:

.. autoclass:: String
   :noindex:

.. autoclass:: Int
   :noindex:

.. autoclass:: Float
   :noindex:

.. autoclass:: Bool
   :noindex:

.. autoclass:: List
   :noindex:

These are all constructed with at least a description. ``default`` and
``secure`` are optional.

Flags must be declared at module level, and can only be declared
once. Redefining a flag results in an error.

.. code-block:: python
   :caption: Example primitive flags.
  
   FLAGS.some_int = flag.Int('some int value')
   FLAGS.some_string = flag.String('some string value', 'default string')
   FLAGS.some_bool = flag.Bool('secure bool (why?)', secure=True)

Required values are indicated by setting ``default`` to
:py:const:`REQUIRED`.

.. code-block:: python
   :caption: Required flag example.

   FLAGS.required_float = flag.Float('some required float', flag.REQUIRED)

Finally, :py:class:`List` is provided which can be used to define a
flag which is a list (cannot be polymorphic). It requires two
additional arguments: a :py:class:`Var` subclass defining the
primitive type, and a separator:

.. code-block:: python
   :caption: List flag example.

   FLAGS.int_list = flag.List(flag.Int, ',', 'a list of integer values')

Using flag values in Python
===========================

Getting
-------

Flag values can be read directly from the
:py:class:`NamespaceFlagSet` object (``FLAGS`` above).

.. code-block:: python
   :caption: Accessing flag values.

   FLAGS.some_int = flag.Int('some int value')
 
   print FLAGS.some_int * 10

Setting
-------

Setting is almost the same, but values should be parseable strings,
not raw values (since the setter is how the various parsers actually
set the values).

.. doctest::
   
   >>> FLAGS.some_int = '42'
   >>> FLAGS.some_int
   42

Positional Arguments
--------------------

Finally, the flag module may expose positional arguments if a
command-line was parsed. These are available via :py:func:`args`:

.. autofunction:: args
   :noindex:

Parsing in ``__main__``
=======================

There are three parsers provided, a command-line parser, an environment
parser and a parser based on :py:mod:`ConfigParser`.

.. autofunction:: parse_commandline
   :noindex:

.. autofunction:: parse_environment
   :noindex:

.. autofunction:: parse_ini
   :noindex:
                  
Flag parsing must be done explicitly. Each parser can be used
independently or with another parser. It is suggested to use the
environment parser first followed by the command-line parser, since
the environment parser can read SECURED\_ settings, and flags can
further be overridden by the command line.

.. code-block:: python
   :caption: Parser Usage.

   import os
   import sys
 
   from oscar import flag
 
   if __name__ == '__main__':
       flag.parse_environment(os.environ.items())
       flag.parse_commandline(sys.argv[1:])

The :py:mod:`ConfigParser` parser requires an object providing
:py:meth:`readline`, which includes a standard opened file.

Note that required flags must be explicitly checked via
:py:func:`die_on_missing_required`. If a config file is read, but the
path to that config file can be set on the command line, it is useful
to refrain from checking if required flags have been set until after
the config file is parsed.

.. code-block:: python
   :caption: Config-file flag.

   import os
   import sys

   from oscar import flag

   FLAGS = flag.namespace(__name__)
   FLAGS.config_file = flag.String('path to config file')

   if __name__ == '__main__':
       flag.parse_commandline(sys.argv[1:])
       if FLAGS.config_file:
           with open(FLAGS.config_file) as config:
               flag.parse_ini(config)
       die_on_missing_required()

Setting Flags from The Outside
==============================

Short Names and Full Names
--------------------------

All flags are fully namespaced and are available by referencing them
through their module path. For instance, if a flag ``baz`` is declared
in module ``foo.bar``, it can be referenced on the command line or in
the environment through ``foo.bar.baz``.

As a convenience, any uniquely named flag can be referenced on the
command line or in the environment through a short name. The short name
is for convenience and should not be used in scripts or configuration
files. Referencing an ambiguous short name will raise a
:py:exc:`KeyError`.

Environment Variables
---------------------

If :py:func:`parse_environment` is called on
:py:meth:`os.environ.items`, environment variables will be mapped onto
flags. As noted, the environment parser supports short and full names.

The environment parser will recognize SECURED\_SETTING\_* environment
variables. These are base64 decoded and set on the appropriate flag if
present (while also setting the ``secure`` attribute on the flag to
:py:obj:`True`).

The environment parser will ignore extraneous environment variables
that do not map to a flag.

.. note:: 

   The last parse method called may overwrite flags set by previous
   parse methods. It is probably preferable to call
   :py:func:`parse_environment` before calling
   :py:func:`parse_commandline`.

Command Line
------------

Command-line flags are expected to precede any positional
arguments. The presence of a single "--" argument can be used to
denote the end of command-line flags. A single "-" or a double "--"
are equivalent in denoting a flag. A flag and its value can be
separated into separate arguments (i.e. via whitespace on the
command line) or a single "=".

.. code-block:: shell
   :caption: Command-line examples.

   # A single '-' is acceptable.
   $ ./my_bin.pex -foo=bar
   $ ./my_bin.pex -foo bar
   # A double '--' is also acceptable.
   $ ./my_bin.pex --foo=bar
   $ ./my_bin.pex --foo bar
   # Everything after '--' becomes a positional argument.
   $ ./my_bin.pex -- --foo --bar --baz

:py:class:`Bool` flags are special-cased in the command-line parser. A
standalone :py:class:`Bool` flag with no value indicates
:py:obj:`True`. A :py:class:`Bool` flag can only be set explicitly
using "=", and a space between the flag and the value is
invalid. Valid boolean values are any case folded variation of
``yes``, ``true``, ``on``, ``1`` for :py:obj:`True`, and ``no``,
``false``, ``off``, ``0`` for :py:obj:`False`. Other values result in
an error.

.. code-block:: shell
   :caption: Boolean special case command-line parsing.

   ./my_bin.pex --some_bool  # some_bool is set to True
   ./my_bin.pex --some_bool=False  # some_bool is set to False
   ./my_bin.pex --some_bool False  # this is invalid and will throw a parse error

Command-line flags also may be referenced by their short name if it's
non-ambiguous, though this is provided as a shortcut for users, and
the fully qualified flag name should be used in configuration and
scripting.

Finally, if any flags are encountered that do not map to a flag in the
application, an error will be raised. All command-line flags must map
to a declared flag.

:py:mod:`ConfigParser` ini files
--------------------------------

There is also support for ini files. Sections map to namespaces, and
key/value pairs within the sections map to flags within those
namespaces.

.. code-block:: ini
   :caption: example.ini

   [__main__]
   output=output.txt

   [utils.zookeeper]
   ensemble=zookeeper-1,zookeeper-2,zookeeper-3

The ini parser will need to be ran against a file-like object.

.. code-block:: python
   :caption: Using :py:func:`parse_ini`.

   with open('~/.config.ini') as config:
       flag.parse_ini(config)

Finally, every section and key/value within an ini file must map to a
namespace and flag. Unexpected sections and keys will raise an error.

Additional Public API for flag
==============================

.. autodata:: GLOBAL_FLAGS
   :noindex:

   .. attribute:: GLOBAL_FLAGS.usage

      This attribute can be replaced with a function that will print
      usage (invoked automatically by --help on the command line). The
      function accepts a single parameter: the
      :py:class:`GlobalFlagSet` object calling it. The default
      implementation calls
      :py:meth:`GlobalFlagSet.write_flags`. Default value is
      :py:func:`default_usage`.

   .. attribute:: GLOBAL_FLAGS.usage_long

      This attribute can be replaced with a function that will print
      long usage (invoked automatically by --helplong on the command
      line). The function accepts a single parameter: the
      :py:class:`GlobalFlagSet` object calling it. The default
      implementation calls
      :py:meth:`GlobalFlagSet.write_flags_long`. Default value is
      :py:func:`default_usage_long`.

   .. automethod:: GlobalFlagSet.visit
      :noindex:

   .. automethod:: GlobalFlagSet.visit_all
      :noindex:
