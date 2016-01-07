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
