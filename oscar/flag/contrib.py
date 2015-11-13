from dateutil import parser

from oscar import flag


class Datetime(flag.Var):

    """A datetime-valued flag."""

    def set(self, value):
        # pylint: disable=attribute-defined-outside-init
        self.value = parser.parse(value)
        if self.value.tzinfo is None:
            raise ValueError("Datetime string '%s' MUST have time zone info" % value)
