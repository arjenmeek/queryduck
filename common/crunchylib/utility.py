import base64
import datetime

from uuid import UUID

from .exceptions import GeneralError


class StatementReference(object):
    """A reference to a Statement that probably requires another resources to resolve."""

    def __init__(self, uuid_):
        """Initialize this as a UUID-based reference."""
        self.uuid = uuid_
        self.self_reference = False
        self.is_statement = True

    def resolve(self, context, statement_repository):
        """Resolve the reference using the provided resources."""
        if self.self_reference or (context is not None and self.uuid == context.uuid):
            return context
        else:
            statement = statement_repository.get_by_uuid(self.uuid)
            return statement


class BlobReference(object):

    is_blob = True

    def __init__(self, identifier):
        self.checksum = base64.b64decode(identifier)
        self.is_blob = True

    def get_identifier(self):
        return base64.b64encode(self.checksum).decode('utf-8')

    def resolve(self, statement_repository):
        """Resolve the reference using the provided resources."""
        blob = statement_repository.get_blob(self.checksum)
        return blob

class ColumnReference(object):
    """A reference to a result column in a query, for comparisons and sorting"""

    def __init__(self, alias, column):
        self.alias = alias
        self.column = column


class SelfReference(StatementReference):
    """A type of StatementReference to use where one element of a Statement refers to the Statement itself."""

    def __init__(self):
        """Initialize this as a reference to the enveloping Statement."""
        self.uuid = None
        self.self_reference = True


def serialize_value(value):
    """Provide a string representation of the value."""
    if value is None:
        return None
    elif type(value) == UUID:
        return 'uuid:{}'.format(str(value))
    elif type(value) == int:
        return 'int:{}'.format(value)
    elif type(value) == str:
        return 'str:{}'.format(value)
    elif type(value) == datetime.datetime:
        return 'datetime:{}'.format(datetime.datetime.strftime(value, '%Y-%m-%dT%H:%M:%S.%f'))
    elif type(value) == SelfReference:
        return 'special:self'
    elif type(value) == ColumnReference:
        return 'column:{}.{}'.format(value.alias, value.column)
    elif hasattr(value, 'is_statement') and value.is_statement:
        return 'st:{}'.format(value.uuid)
    elif hasattr(value, 'is_blob') and value.is_blob:
        return 'blob:{}'.format(value.get_identifier())


def deserialize_value(value):
    """Decode a string representation of a value into either the proper value or a resolvable reference."""
    type_str, value_str = value.split(':', 1)
    if type_str == 'uuid':
        return UUID(value_str)
    elif type_str == 'st':
        uuid_ = UUID(value_str)
        return StatementReference(uuid_=uuid_)
    elif type_str == 'blob':
        return BlobReference(identifier=value_str)
    elif type_str == 'int':
        return int(value_str)
    elif type_str == 'str':
        return str(value_str)
    elif type_str == 'datetime':
        return datetime.datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S.%f')
    elif type_str == 'special' and value_str == 'self':
        return SelfReference()
    elif type_str == 'column':
        alias, column = value_str.split('.')
        return ColumnReference(alias, column)

def get_value_type(value):
    if value is None:
        return None
    elif type(value) == UUID:
        return 'uuid'
    elif type(value) == int:
        return 'integer'
    elif type(value) == str:
        return 'string'
    elif type(value) == datetime.datetime:
        return 'datetime'
    elif hasattr(value, 'is_statement') and value.is_statement:
        return 'statement'.format(value.uuid)
