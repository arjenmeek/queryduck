import base64
import datetime
import uuid

from collections import defaultdict

from .exceptions import CVValueError
from .types import Statement, Blob


value_types = {
    'int': {
        'type': int,
        'factory': int,
        'column_name': 'object_integer',
        'serializer': str,
    },
    'bool': {
        'type': bool,
        'factory': bool,
        'column_name': 'object_boolean',
        'serializer': str,
    },
    'float': {
        'type': float,
        'factory': float,
        'column_name': 'object_float',
        'serializer': str,
    },
    'str': {
        'type': str,
        'factory': str,
        'column_name': 'object_string',
        'serializer': str,
    },
    'datetime': {
        'type': datetime.datetime,
        'factory': lambda dt: datetime.datetime.fromisoformat(dt),
        'column_name': 'object_datetime',
        'serializer': lambda dt: dt.isoformat(),
    },
    's': {
        'type': Statement,
        'factory': Statement,
        'column_name': 'object_statement_id',
        'serializer': lambda s: s.uuid,
    },
    'blob': {
        'type': Blob,
        'factory': Blob,
        'column_name': 'object_blob_id',
        'serializer': lambda b: b.encoded_sha256(),
    },
    'none': {
        'type': type(None),
        'factory': lambda x: None,
        'column_name': 'id', # for "IS NULL" comparison
        'serializer': str,
    }
}

value_types_by_native = {
    int: 'int',
    bool: 'bool',
    float: 'float',
    str: 'str',
    datetime.datetime: 'datetime',
    Statement: 's',
    Blob: 'blob',
    type(None): 'none',
}

value_comparison_methods = {
    'eq': '__eq__',
    'ne': '__ne__',
    'gt': '__gt__',
    'ge': '__ge__',
    'lt': '__lt__',
    'le': '__le__',
    'contains': 'contains',
    'startswith': 'startswith',
    'endswith': 'endswith',
}

list_comparison_methods = {
    'in': 'in_',
}


def _process_db_row(db_row, db_columns, db_entities):
    for try_vtype, options in value_types.items():
        column = db_columns[options['column_name']]
        db_value = db_row[column]
        if db_value is None or try_vtype == 'none':
            continue
        vtype = try_vtype
        break
    else:
        raise CVValueError

    if vtype == 's':
        uuid_ = db_row[db_entities['s'].c.uuid]
        v = Statement(uuid_=uuid_, id_=db_value)
    elif vtype == 'blob':
        sha256 = db_row[db_entities['blob'].c.sha256]
        v = Blob(sha256=sha256, id_=db_value)
    else:
        v = db_value

    return v, vtype

def _get_native_vtype(native_value):
    vtype = value_types_by_native[type(native_value)]
    return vtype

def _process_serialized_value(serialized_value):
    vtype, ser_v = serialized_value.split(':', 1)
    if not vtype in value_types:
        raise CVValueError("Invalid value type: {}".format(vtype))
    v = value_types[vtype]['factory'](ser_v)
    return v, vtype

def serialize(native_value):
    vtype = _get_native_vtype(native_value)
    serialized = '{}:{}'.format(vtype, value_types[vtype]['serializer'](native_value))
    return serialized

def deserialize(serialized_value):
    v, vtype = _process_serialized_value(serialized_value)
    return v


class Value:

    def __init__(self, serialized=None, native=None, db_columns=None, db_row=None, db_entities=None):
        if serialized is not None:
            self.v, self.vtype = _process_serialized_value(serialized)
        elif native is not None:
            self.vtype = _get_native_vtype(native)
            self.v = native
        elif db_columns is not None and db_row is not None:
            self.v, self.vtype = _process_db_row(db_row, db_columns, db_entities)
        self.column_name = value_types[self.vtype]['column_name']
        self.serializer = value_types[self.vtype]['serializer']

    @classmethod
    def native(cls, native_value):
        return cls(native=native_value)

    def __repr__(self):
        return '<Value type={} v={}>'.format(self.vtype, self.v)

    def db_value(self):
        if self.vtype in ('s', 'blob'):
            return self.v.id
        else:
            return self.v

    def column_compare(self, op, columns):
        column = columns[self.column_name]
        op_method = value_comparison_methods[op]
        return getattr(column, op_method)(self.db_value())

    def serialize(self):
        return '{}:{}'.format(self.vtype, self.serializer(self.v))


class ValueList:

    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return 'ValueList {}>'.format(self.values)

    def column_compare(self, op, columns):
        column = columns[self.values[0].column_name]
        op_method = list_comparison_methods[op]
        db_values = [v.db_value() for v in self.values]
        return getattr(column, op_method)(db_values)
