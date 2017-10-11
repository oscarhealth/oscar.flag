import datetime
import logging
import unittest

import six
from dateutil import tz

from oscar import flag
from oscar.flag import contrib

# pylint: disable=wrong-import-position,ungrouped-imports
six.add_move(six.MovedModule('mock', 'mock', 'unittest.mock'))
from six.moves import mock


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


class DateFlagTest(unittest.TestCase):

    def test_set_good_value(self):
        date_flag = contrib.Date('some datetime', default=flag.REQUIRED)
        date_flag.set('11-01-2015')
        expected = datetime.date(year=2015, month=11, day=1)
        self.assertEqual(date_flag.value, expected)

    def test_set_bad_value(self):
        date_flag = contrib.Date('some datetime', default=flag.REQUIRED)
        with self.assertRaises(ValueError):
            date_flag.set('11-01-b2015')


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


class JsonTest(unittest.TestCase):

    def test_default_value(self):
        json_flag = contrib.Json('help text', {})
        self.assertEqual(json_flag.get(), {})
        json_flag = contrib.Json('help text', [1, 2, 3])
        self.assertEqual(json_flag.get(), [1, 2, 3])

    def test_set_good_value(self):
        json_flag = contrib.Json('help text')
        json_flag.set('["foo", "bar", "baz"]')
        self.assertEqual(json_flag.get(), ['foo', 'bar', 'baz'])

    def test_set_bad_value(self):
        json_flag = contrib.Json('help text')
        with self.assertRaises(ValueError):
            json_flag.set('huh')


class LogLevelTest(unittest.TestCase):

    def test_default(self):
        with mock.patch('logging.getLogger') as mock_get_logger:
            level_flag = contrib.LogLevel('foo', 'foo level', default='INFO')
        mock_get_logger.return_value.setLevel.assert_called_once_with(logging.INFO)
        self.assertEqual(level_flag.get(), logging.INFO)

        with mock.patch('logging.getLogger') as mock_get_logger:
            level_flag = contrib.LogLevel('foo', 'foo level', default='critical')
        mock_get_logger.return_value.setLevel.assert_called_once_with(logging.CRITICAL)
        self.assertEqual(level_flag.get(), logging.CRITICAL)

    def test_set(self):
        level_flag = contrib.LogLevel('foo', 'foo level')
        with mock.patch('logging.getLogger') as mock_get_logger:
            level_flag.set('critical')
        mock_get_logger.return_value.setLevel.assert_called_once_with(logging.CRITICAL)
        self.assertEqual(level_flag.get(), logging.CRITICAL)

    def test_invalid(self):
        level_flag = contrib.LogLevel('foo', 'foo level')
        with self.assertRaises(ValueError):
            level_flag.set('garbage')
