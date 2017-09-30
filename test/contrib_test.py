import datetime
import unittest

from dateutil import tz
import six

from oscar import flag
from oscar.flag import contrib


class DatetimeFlagTest(unittest.TestCase):

    def test_no_timezone_fail(self):
        datetime_flag = contrib.Datetime('some datetime',
                                         default=flag.REQUIRED)
        with self.assertRaises(ValueError):
            datetime_flag.set('22:00:00')

    def test_timezone_success(self):
        datetime_flag = contrib.Datetime('some datetime',
                                         default=flag.REQUIRED)
        datetime_flag.set('11-01-2015 22:30:01 +00:00')
        expected = datetime.datetime(year=2015, month=11, day=1,
                                     hour=22, minute=30, second=1,
                                     tzinfo=tz.tzutc())
        self.assertEqual(datetime_flag.value, expected)


class ChoicesTest(unittest.TestCase):

    def test_default_value(self):
        contrib.Choices(flag.Int, 'pick a number', [1, 2, 3], 1)
        contrib.Choices(flag.Int, 'pick a number', [1, 2, 3], flag.REQUIRED)
        with self.assertRaises(flag.FlagException):
            contrib.Choices(flag.Int, 'pick a number', [1, 2, 3])

    def test_good_choice(self):
        choices = contrib.Choices(flag.Int, 'pick a number', [1, 2, 3], 1)
        choices.set('1')
        self.assertEqual(choices.get(), 1)

    def test_bad_choice(self):
        choices = contrib.Choices(flag.Int, 'pick a number', [1, 2, 3], 1)
        with self.assertRaises(ValueError):
            choices.set('4')

    def test_long_description(self):
        flagset = flag.GlobalFlagSet()
        flags = flagset.namespace('test')
        flags.choices = contrib.Choices(flag.Int, 'pick a number', [1, 2, 3], 1)
        out = six.StringIO()
        flagset.write_flags(out, 'test')
        self.assertEqual(out.getvalue(), (
            '    [test.]choices=1: pick a number (Int)\n' +
            '        1\n' +
            '        2\n' +
            '        3\n'))
