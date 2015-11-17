# pylint: disable=W0621
import base64
import ConfigParser
import sys


class _Required(object):

    def __str__(self):
        return '<required>'

REQUIRED = _Required()
UNSET = object()


def default_usage(globalflags):
    '''Default for printing out usage.

    :type globalflags: GlobalFlagSet
    '''
    sys.stderr.write('Usage of %s:\n' % sys.argv[0])
    globalflags.write_flags(sys.stderr)
    sys.exit(0)


def default_usage_long(globalflags, return_code=0):
    '''Default for printing out long-form usage.

    :type globalflags: GlobalFlagSet
    '''
    sys.stderr.write('Usage of %s:\n' % sys.argv[0])
    globalflags.write_flags_long(sys.stderr)
    sys.exit(return_code)


class GlobalFlagSet(object):

    '''GlobalFlagSet is a collection of namespaces and flag logic.'''

    def __init__(self, usage=default_usage, usage_long=default_usage_long):
        '''Create a new GlobalFlagSet.

        :type usage: F(GlobalFlagSet)
        :type usage_long: G(GlobalFlagSet)
        '''
        self.usage = usage
        self.usage_long = usage_long
        self.namespace_flags = dict()
        self.args = []

    def namespace(self, namespace):
        '''Returns a :class:`NamespaceFlagSet` associated with ``namespace``.

        :type namespace: str
        :rtype: NamespaceFlagSet
        '''
        return self.namespace_flags.setdefault(namespace, NamespaceFlagSet())

    def get(self, namespace, flag):
        '''get the flag object associated with ``flag`` in ``namespace``.

        :type namespace: str
        :type flag: str
        :rtype: Var
        :raises KeyError: if the flag is not found
        '''
        return self.namespace_flags[namespace]._flags[flag]

    def find_short(self, flag):
        '''Find the namespace for a non-qualified ``flag``.

        If the ``flag`` is not found or multiple flags are found,
        :exc:`KeyError` is raised.

        :type flag: str
        :rtype: str
        :raises KeyError: if the flag is not found or ambiguous
        '''
        matches = []
        for namespace, flagset in self.namespace_flags.items():
            if flag in flagset._flags:
                matches.append(namespace)
        if len(matches) > 1:
            raise KeyError('ambiguous flag \'%s\' in namespaces %s' % (flag, matches))
        if len(matches) == 0:
            raise KeyError('%s' % flag)
        return matches[0]

    def write_flags(self, out, namespace='__main__'):
        '''Prints the usage to ``out``.

        :type out: file
        :type namespace: str
        '''
        for name, var in sorted(self.namespace(namespace)._flags.items()):
            try:
                _ = self.find_short(name)
            except KeyError:
                out.write('    -%s.%s=%s: %s (%s)\n' % (
                    namespace, name, var.default, var.description, var.type_str))
            else:
                out.write('    [%s.]%s=%s: %s (%s)\n' % (
                    namespace, name, var.default, var.description, var.type_str))

    def write_flags_long(self, out):
        '''Prints all flag usage to ``out``.

        :type out: file
        '''
        for namespace in sorted(self.namespace_flags):
            out.write('%s:\n' % namespace)
            self.write_flags(out, namespace)
            out.write('\n')

    def visit(self, func):
        '''Walk all *set* flags, calling ``func`` on each.

        :type func: F(str, str, Var)
        :param func: visiting function
        '''
        for namespace in sorted(self.namespace_flags):
            for name, flag in sorted(self.namespace(namespace)._flags.items()):
                if flag.is_set():
                    func(namespace, name, flag)

    def visit_all(self, func):
        '''Walk all flags, calling ``func`` on each.

        :type func: F(str, str, Var)
        :param func: visiting function
        '''
        for namespace in sorted(self.namespace_flags):
            for name, flag in sorted(self.namespace(namespace)._flags.items()):
                func(namespace, name, flag)

    def check_required(self):
        '''Returns a list of ``(namespace, name, flag)`` of all unset, required flags.

        :rtype: list[tuple(str, str, Var)]
        '''
        nonset = []

        def _check(namespace, name, flag):
            if flag.default is REQUIRED and not flag.is_set():
                nonset.append((namespace, name, flag))
        self.visit_all(_check)
        return nonset

    def parse_commandline(self, args):
        '''Parse a commandline into flags and arguments.

        Parse a commandline. a single '-' and a double '--' are
        treated as equivalent for denoting a flag. Flag values may be
        separated by '=' or be the next argument. Booleans are a
        special case that indicate a true value or must have their
        values separated by '='.

        :type args: list(str)
        :raises KeyError: on unknown flag
        :raises ParseException: on invalid command-line syntax
        '''
        self.args = args
        while len(self.args):
            arg = self.args[0]
            if len(arg) == 0 or arg[0] != '-' or len(arg) == 1:
                break
            num_minuses = 1
            if arg[1] == '-':
                num_minuses += 1
                if len(arg) == 2:
                    # -- terminates flag list (rest are args).
                    self.args = self.args[1:]
                    break
            name = arg[num_minuses:]
            if len(name) == 0 or name[0] == '-' or name[0] == '=':
                raise ParseException('bad flag syntax: %s' % arg)
            self.args = self.args[1:]
            has_value = False
            value = ''
            for i in range(1, len(name)):
                if name[i] == '=':
                    value = name[i + 1:]
                    has_value = True
                    name = name[0:i]
                    break
            if name == 'help' or name == 'h':
                self.usage(self)
            if name == 'helplong':
                self.usage_long(self)
            if '.' not in name:
                namespace = self.find_short(name)
            else:
                parts = name.split('.')
                namespace, name = '.'.join(parts[:-1]), parts[-1]
            flag = self.get(namespace, name)
            if isinstance(flag, Bool):
                if has_value:
                    flag.set(value)
                else:
                    flag.set('True')
            else:
                if not has_value and len(self.args) > 0:
                    has_value = True
                    value, self.args = self.args[0], self.args[1:]
                if not has_value:
                    raise ParseException('flag needs an argument: %s' % name)
                flag.set(value)

    def parse_environment(self, args):
        '''Parse environment variable tuples.

        Call with os.environ:
          >>> import os
          >>> flag.parse_environment(os.environ.items())

        Recognizes `SECURED_SETTING_` prefixed flags, translates from
        base64 and maps to the short name. `secure` is also set to
        `True` on the underlying flag object, which should be
        respected by users of :meth:`visit` and :meth:`visit_all`.

        :type args: list[tuple(str, str)]
        '''
        for name, value in args:
            # First treat SECURED_SETTING_ values specially.
            secure = False
            if name.startswith('SECURED_SETTING_'):
                name = name[len('SECURED_SETTING_'):]
                value = base64.b64decode(value)
                secure = True
            try:
                if '.' not in name:
                    namespace = self.find_short(name)
                else:
                    parts = name.split('.')
                    namespace, name = '.'.join(parts[:-1]), parts[-1]
                flag = self.get(namespace, name)
                flag.set(value)
                flag.secure = secure
            except KeyError:
                # Ignore environment variables that don't map to a setting.
                pass

    def parse_ini(self, file_p):
        '''Parse a :mod:`ConfigParser` compatible file object.

        Namespaces are section headers, keys are flags::

          [__main__]
          foo=bar

          [foo.bar]
          baz=42

        ``file_p`` only needs to implement ``readline(size=0)``.

        :type file_p: file
        '''
        config = ConfigParser.ConfigParser()
        config.readfp(file_p)
        for section in config.sections():
            for name, value in config.items(section):
                self.get(section, name).set(value)


class NamespaceFlagSet(object):

    '''Represents a set of flags in a namespace.'''

    def __init__(self):
        '''Create a new :class:`NamespaceFlagSet`.'''
        self.__dict__['_flags'] = dict()

    def __getattr__(self, name):
        '''Return the value for a flag.

        :type name: str
        :rtype: Var
        '''
        return self._flags[name].get()

    def __setattr__(self, name, value):
        '''Set a flag accessor if none exists else return a flag value.

        :type name: str
        :type value: str or Var

        :raises FlagException: on flag redefinition or invalid definition
        '''
        if name in self.__dict__:
            self.__dict__[name] = value
            return
        if name in self._flags:
            if isinstance(value, Var):
                raise FlagException('%s was already defined' % name)
            self._flags[name].set(value)
        else:
            if not isinstance(value, Var):
                raise FlagException('%s is not a flag.Var' % name)
            self._flags[name] = value


class FlagException(Exception):

    '''Error in flag initialization or access.'''


class ParseException(Exception):

    '''Error in command-line parsing.'''


class Var(object):

    '''Base of all flag accessors.'''

    value = UNSET
    type_str = 'Unknown'

    def __init__(self, description, default=None, secure=False):
        '''Create a new Var flag accessor.

        :type description: str
        :type default: None or _Required of object or T
        :type secure: bool
        '''
        self.description = description
        self.default = default
        self.secure = secure

    def get(self):
        '''Return the flag value, or default if it is not set.'''
        return self.value if self.is_set() else self.default

    def is_set(self):
        '''
        :rtype: bool
        '''
        return self.value is not UNSET


class String(Var):

    '''String-valued flag.'''

    type_str = 'String'

    def set(self, value):
        self.value = value


class Int(Var):

    '''Integer-valued flag.'''

    type_str = 'Int'

    def set(self, value):
        self.value = int(value)


class Float(Var):

    '''Float-valued flag.'''

    type_str = 'Float'

    def set(self, value):
        self.value = float(value)


class Bool(Var):

    '''Boolean-valued flag.'''

    type_str = 'Bool'

    def set(self, value):
        if value.lower() in ('t', 'true', 'yes', 'on', '1'):
            self.value = True
        elif value.lower() in ('f', 'false', 'no', 'off', '0'):
            self.value = False
        else:
            raise ValueError(value)


class List(Var):

    '''Flag that is a list of another flag type.'''

    type_str = 'List[_]'

    def __init__(self, inner_type, separator, description, default=None, secure=False):
        '''Create a list flag of `inner_type`.

        E.g.:
        >>> int_list = List(Int, ',', 'List of integers.')
        >>> int_list.set('1,2,3,4,5')
        >>> int_list.get()
        [1, 2, 3, 4, 5]

        :type inner_type: type
        :type separator: str
        :type description: str
        :type default: list or None or _Required
        :type secure: bool
        '''
        default = [] if default is None else default
        super(List, self).__init__(description, default, secure)
        self.separator = separator
        self.inner_value = inner_type(description, default, secure)
        self.type_str = 'List[%s]' % self.inner_value.type_str

    def set(self, value):
        '''
        :type value: str
        '''
        self.value = []
        for part in value.split(self.separator):
            self.inner_value.set(part)
            self.value.append(self.inner_value.get())


# Default functions that use the default flagset.
GLOBAL_FLAGS = GlobalFlagSet()


def namespace(name):
    '''Return a namespace from :const:`GLOBAL_FLAGS`.

    :type name: str
    :rtype: NamespaceFlagSet
    '''
    return GLOBAL_FLAGS.namespace(name)


def parse_commandline(args):
    '''Parse commandline ``args`` with :const:`GLOBAL_FLAGS`.

    :type args: list[str]
    '''
    GLOBAL_FLAGS.parse_commandline(args)


def parse_environment(args):
    '''Parse environment ``args`` with :const:`GLOBAL_FLAGS`.

    :type args: list[tuple(str, str)]
    '''
    GLOBAL_FLAGS.parse_environment(args)


def parse_ini(file_p):
    '''Parse a :mod:`ConfigParser` compatible file with :const:`GLOBAL_FLAGS`.

    :type file_p: file
    '''
    GLOBAL_FLAGS.parse_ini(file_p)


def args():
    '''Return positional ``args`` from :const:`GLOBAL_FLAGS`.

    :rtype: list[str]
    '''
    return GLOBAL_FLAGS.args


def die_on_missing_required():
    '''If missing required flags, die and write usage.'''
    nonset = GLOBAL_FLAGS.check_required()
    if nonset:
        sys.stderr.write('Missing required flags:\n')
        for namespace, name, _ in nonset:
            sys.stderr.write('    [%s.]%s\n' % (namespace, name))
        GLOBAL_FLAGS.usage_long(GLOBAL_FLAGS, return_code=1)
