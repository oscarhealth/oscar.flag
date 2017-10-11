import json
import logging

import six
from dateutil import parser

from oscar import flag


class Datetime(flag.Var):

    '''Datetime-valued flag.'''

    type_str = 'Datetime'

    def set(self, value):
        # pylint: disable=attribute-defined-outside-init
        self.value = parser.parse(value)
        if self.value.tzinfo is None:
            raise ValueError('Datetime string "%s" MUST have time zone info' % value)


class Date(flag.Var):

    '''Date-valued flag.'''

    type_str = 'Date'

    def set(self, value):
        # pylint: disable=attribute-defined-outside-init
        self.value = parser.parse(value).date()


class Choices(flag.Var):

    '''Flag with a set of choices.'''

    def __init__(self, inner_type, description, choices, default=None, secure=False):
        if default is not flag.REQUIRED and default not in choices:
            raise flag.FlagException('default value must be a valid choice or REQUIRED')
        super(Choices, self).__init__(description, default, secure)
        self.inner_value = inner_type(description, default, secure)
        self.type_str = inner_type.type_str
        self.choices = choices
        self.long_description = '\n'.join(str(x) for x in choices)

    def set(self, value):
        # pylint:disable=attribute-defined-outside-init
        self.inner_value.set(value)
        self.value = self.inner_value.get()
        if self.value not in self.choices:
            raise ValueError('%s not a valid value' % value)


class Json(flag.Var):

    '''Flag that takes valid JSON string'''

    type_str = 'JSON'

    def set(self, value):
        self.value = json.loads(value)


class LogLevel(flag.Var):

    '''Flag that lets you specify the logging level for a given logger.
    Automatically converts log level names to symbolic values::

        from oscar.flag import contrib as flag_contrib

        FLAGS.log_level = flag_contrib.LogLevel(
            __name__, 'log level for loggers in this module')
        FLAGS.sqlalchemy_log_level = flag_contrib.LogLevel(
            'sqlalchemy.engine', 'log level for sqlalchemy')
    '''

    class Level(flag.Var):
        type_str = 'String'

        def coerce(self, value):
            level = logging.getLevelName(value.upper())
            if not isinstance(level, six.integer_types):
                raise ValueError('Unknown log level: %r' % level)
            return level

        def get(self):
            return self.value if self.is_set() else self.coerce(self.default)

        def set(self, value):
            self.value = self.coerce(value)

    def __init__(self, name, description, default=None):
        super(LogLevel, self).__init__(description, default, False)
        inner_type = self.Level
        self.logger_name = name
        self.inner_value = inner_type(description, default, False)
        self.type_str = inner_type.type_str

        choices = {logging.CRITICAL, logging.FATAL, logging.ERROR,
                   logging.WARNING, logging.WARN, logging.INFO, logging.DEBUG}
        self.long_description = '\n'.join(
            logging.getLevelName(x) for x in choices)

        if default is not None:
            self.set(default)

    def set(self, value):
        self.inner_value.set(value)
        self.value = self.inner_value.get()
        logging.getLogger(self.logger_name).setLevel(self.value)

    def __str__(self):
        return logging.getLevelName(self.value)
