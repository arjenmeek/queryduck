import base64
import datetime

from uuid import UUID

from .exceptions import GeneralError


def deserialize_value(value):
    """Decode a string representation of a value into either the proper value or a resolvable reference."""
    type_str, value_str = value.split(':', 1)
    if type_str == 'uuid':
        return UUID(value_str)
    elif type_str == 'st':
        uuid_ = UUID(value_str)
        return {'uuid': UUID(value_str)}
    elif type_str == 'blob':
        return {'hash': value_str}
    elif type_str == 'int':
        return int(value_str)
    elif type_str == 'float':
        return float(value_str)
    elif type_str == 'str':
        return str(value_str)
    elif type_str == 'datetime':
        return datetime.datetime.strptime(value_str, '%Y-%m-%dT%H:%M:%S.%f')
    elif type_str == 'bool':
        return (value_str.lower()[0] in ('t', 'y', '1'))

def serialize_value(value):
    """Provide a string representation of the value."""
    if value is None:
        return None
    elif type(value) == UUID:
        return 'uuid:{}'.format(str(value))
    elif type(value) == int:
        return 'int:{}'.format(value)
    elif type(value) == float:
        return 'float:{}'.format(value)
    elif type(value) == str:
        return 'str:{}'.format(value)
    elif type(value) == datetime.datetime:
        return 'datetime:{}'.format(datetime.datetime.strftime(value, '%Y-%m-%dT%H:%M:%S.%f'))
    elif type(value) == bool:
        return 'bool:{}'.format(value)
    elif type(value) == dict and 'uuid' in value:
        return 'st:{}'.format(value['uuid'])
    elif type(value) == dict and 'hash' in value:
        return 'blob:{}'.format(value['hash'])

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
