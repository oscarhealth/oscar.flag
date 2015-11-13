# pylint: disable=C0103
import base64
import io
import unittest

from oscar import flag


class CommandLineTest(unittest.TestCase):

    def setUp(self):
        self.FLAGS = flag.GlobalFlagSet()

    def test_empty(self):
        args = []
        self.FLAGS.parse_commandline(args)
        self.assertEqual(self.FLAGS.args, [])
        self.assertEqual(self.FLAGS.check_required(), [])

    def test_missing_required(self):
        args = []
        flags = self.FLAGS.namespace('bar')
        foo = flag.String("some flag", flag.REQUIRED)
        flags.foo = foo
        self.FLAGS.parse_commandline(args)
        self.assertEqual(self.FLAGS.check_required(), [('bar', 'foo', foo)])

    def test_non_existent(self):
        args = ['--noflag', 'foo']
        self.assertRaises(KeyError, self.FLAGS.parse_commandline, args)

    def test_boolean(self):
        args = ['--foo']
        flags = self.FLAGS.namespace(__name__)
        flags.foo = flag.Bool("foo bool")
        self.FLAGS.parse_commandline(args)
        self.assertEqual(flags.foo, True)

        for t_value in ['t', 'true', 'yes', 'on', '1']:
            args = ['--foo=%s' % t_value]
            self.FLAGS.parse_commandline(args)
            self.assertTrue(flags.foo)
        for f_value in ['f', 'false', 'no', 'off', '0']:
            args = ['--foo=%s' % f_value]
            self.FLAGS.parse_commandline(args)
            self.assertFalse(flags.foo)

    def test_flag_termination(self):
        args = ['--', '--1', '2', '--3']
        self.FLAGS.parse_commandline(args)
        self.assertEqual(args[1:], self.FLAGS.args)

    def test_extra_args(self):
        args = ['--foo', '1', '2', '3']
        flags = self.FLAGS.namespace(__name__)
        flags.foo = flag.Int("foo int")
        self.FLAGS.parse_commandline(args)
        self.assertEqual(args[2:], self.FLAGS.args)

    def test_malformed_flag(self):
        args = ['---foo', '1', '2', '3']
        self.assertRaises(flag.ParseException, self.FLAGS.parse_commandline, args)
        flags = self.FLAGS.namespace(__name__)
        flags.foo = flag.Int("foo int")
        args = ['--foo']
        self.assertRaises(flag.ParseException, self.FLAGS.parse_commandline, args)

    def test_fully_qualified(self):
        args = ['--foo.bar', '0.45']
        flags = self.FLAGS.namespace('foo')
        flags.bar = flag.Float("foo float")
        self.FLAGS.parse_commandline(args)
        self.assertEqual(flags.bar, 0.45)
        # Non-ambiguous short form.
        args = ['--bar', '0.90']
        self.FLAGS.parse_commandline(args)
        self.assertEqual(flags.bar, 0.90)
        # Ambiguous short forms.
        other_flags = self.FLAGS.namespace('bar')
        other_flags.bar = flag.Float("foo float")
        args = ['--bar', '0.90']
        self.assertRaises(KeyError, self.FLAGS.parse_commandline, args)
        # Qualified form of ambiguous short form.
        args = ['--foo.bar', '0.90', '--bar.bar', '1.80']
        self.FLAGS.parse_commandline(args)
        self.assertEqual(flags.bar, 0.90)
        self.assertEqual(other_flags.bar, 1.80)


class EnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.FLAGS = flag.GlobalFlagSet()

    def test_all(self):
        args = [
            ('foo', 'bar'), ('doesnotexist', 'baz'), ('foo.bar', 'blah'),
            ('SECURED_SETTING_SECRET', base64.encodestring('secret_sauce'))]
        flags = self.FLAGS.namespace(__name__)
        foo_flags = self.FLAGS.namespace('foo')
        flags.foo = flag.String("foo string")
        foo_flags.bar = flag.String("bar string")
        flags.SECRET = flag.String("secret string")
        self.FLAGS.parse_environment(args)
        self.assertEqual(flags.foo, 'bar')
        self.assertEqual(foo_flags.bar, 'blah')
        self.assertEqual(flags.SECRET, 'secret_sauce')
        self.assertEqual(self.FLAGS.get(__name__, 'SECRET').secure, True)


class IniTest(unittest.TestCase):

    def setUp(self):
        self.FLAGS = flag.GlobalFlagSet()

    def test_all(self):
        fp = io.BytesIO("""
[foo]
bar = 1.23
baz = hello world
truefalse = no
""")
        flags = self.FLAGS.namespace('foo')
        flags.bar = flag.Float("some float")
        flags.baz = flag.String("some string")
        flags.truefalse = flag.Bool("some bool")
        self.FLAGS.parse_ini(fp)
        self.assertEqual(flags.bar, 1.23)
        self.assertEqual(flags.baz, "hello world")
        self.assertFalse(flags.truefalse)

    def test_bad_ini(self):
        fp = io.BytesIO("""
[doesnotexist]
blah = blah
""")
        self.assertRaises(KeyError, self.FLAGS.parse_ini, fp)


class FlagTypeTest(unittest.TestCase):

    def test_string(self):
        var = flag.String("some string")
        var.set("foo")
        self.assertEqual(var.get(), "foo")

    def test_int(self):
        var = flag.Int("some int")
        var.set("42")
        self.assertEqual(var.get(), 42)

    def test_float(self):
        var = flag.Float("some float")
        var.set("3.1415")
        self.assertEqual(var.get(), 3.1415)

    def test_bool(self):
        var = flag.Bool("some bool")
        for f in ['f', 'false', 'off', 'no', '0']:
            var.set(f)
            self.assertFalse(var.get())
        for t in ['t', 'true', 'on', 'yes', '1']:
            var.set(t)
            self.assertTrue(var.get())

    def test_list(self):
        var = flag.List(flag.Int, ",", "some list")
        self.assertEqual(var.get(), [])
        var.set("1,2,3,4,5")
        self.assertEqual(var.get(), [1, 2, 3, 4, 5])
