import base64
import datetime
import uuid

from collections import defaultdict
from decimal import Decimal

from .exceptions import QDValueError


class Filter:

    def __init__(self, op):
        self.op = op


class Inverted:

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash('INVERTED') ^ hash(self.value)
        if self.uuid is None:
            return hash(self.id)
        return hash(self.uuid)

class Statement:

    def __init__(self, uuid_=None, id_=None, triple=None,
            attribute_loader=None):
        self.uuid = uuid.UUID(uuid_) if type(uuid_) == str else uuid_
        self.id = id_
        self.attributes = defaultdict(list)
        self.triple = triple
        self.attribute_loader = attribute_loader
        self.saved = False

    def __getitem__(self, attr):
        """Make Statement subscriptable"""
        if self.attribute_loader is None:
            raise QDValueError("Attempted to access Statement attribute but no loader is present")
        return self.attribute_loader(self, attr)

    def __hash__(self):
        if self.uuid is None:
            return hash(self.id)
        return hash(self.uuid)

    def __json__(self, request):
        data = {
            'uuid': 'uuid:{}'.format(self.uuid),
            '_ref': 's:{}'.format(self.uuid),
        }
        for k, vlist in self.attributes.items():
            data[k] = []
            for v in vlist:
                data[k].append(v.serialize())
        return data

    def __repr__(self):
        parts = ['{}={}'.format(k, getattr(self, k))
            for k in ('uuid', 'id')
            if getattr(self, k) is not None
        ]
        if self.triple:
            parts.append('complete')
        return '<Statement {}>'.format(' '.join(parts))

    def __eq__(self, other):
        return Comparison(self, 'eq', other)


class Blob:

    def __init__(self, serialized=None, sha256=None, id_=None):
        self.id = id_
        self.sha256 = base64.urlsafe_b64decode(serialized) if sha256 is None else sha256

    def encoded_sha256(self):
        r = None if self.sha256 is None else base64.urlsafe_b64encode(self.sha256).decode('utf-8')
        return r

    def serialize(self):
        return self.encoded_sha256()

    def __repr__(self):
        return '<Blob id={} sha256={}>'.format(self.id, None if self.sha256 is None else self.encoded_sha256())

    def __hash__(self):
        return hash(self.sha256)


class File:

    def __init__(self, serialized=None, volume=None, path=None):
        if serialized:
            ser_opts, self.volume, ser_path = serialized.split(':', 2)
            opts = ser_opts.split(',')
            if 'b64' in opts:
                self.path = base64.urlsafe_b64decode(ser_path)
            else:
                self.path = ser_path.encode()
        else:
            self.volume = volume
            self.path = path

    def __repr__(self):
        return '<File volume="{}" path="{}">'.format(self.volume, self.path.decode())

    def serialize(self):
        try:
            return ':{}:{}'.format(self.volume, self.path.decode())
        except UnicodeDecodeError:
            return 'b64:{}:{}'.format(self.volume, base64.urlsafe_b64encode(self.path).decode())


class Placeholder:

    def __init__(self, id_):
        self.id = id_

    def __repr__(self):
        return '<Placeholder {}>'.format(self.id)


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
    'dec': {
        'type': Decimal,
        'factory': Decimal,
        'column_name': 'object_decimal',
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
        'serializer': lambda b: b.serialize(),
    },
    'none': {
        'type': type(None),
        'factory': lambda x: None,
        'column_name': 'id', # for "IS NULL" comparison
        'serializer': str,
    },
    'file': {
        'type': File,
        'factory': File,
        'serializer': lambda f: f.serialize(),
    },
}

value_types_by_native = {
    int: 'int',
    bool: 'bool',
    Decimal: 'dec',
    float: 'float',
    str: 'str',
    datetime.datetime: 'datetime',
    Statement: 's',
    Blob: 'blob',
    type(None): 'none',
    Filter: 'filter',
    Inverted: 'inverted',
    File: 'file',
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
    'in': 'in_',
}

list_comparison_methods = {
    'in': 'in_',
}


def process_db_row(db_row, db_columns, db_entities):
    for try_vtype, options in value_types.items():
        column = db_columns[options['column_name']]
        db_value = db_row[column]
        if db_value is None or try_vtype == 'none':
            continue
        vtype = try_vtype
        break
    else:
        raise QDValueError("Cannot process DB row {}".format(db_row))

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
        raise QDValueError("Invalid value type: {}".format(vtype))
    v = value_types[vtype]['factory'](ser_v)
    return v, vtype

def serialize(native_value):
    vtype = _get_native_vtype(native_value)
    if vtype == 'filter':
        return native_value.op
    elif vtype == 'inverted':
        return '~{}'.format(serialize(native_value.value))
    serialized = '{}:{}'.format(vtype, value_types[vtype]['serializer'](native_value))
    return serialized

def deserialize(serialized_value):
    v, vtype = _process_serialized_value(serialized_value)
    return v

def prepare_for_db(native_value):
    vtype = _get_native_vtype(native_value)
    if vtype in ('s', 'blob'):
        value = native_value.id
    else:
        value = native_value
    return value, value_types[vtype]['column_name']

def column_compare(value, op, columns):
    vtype = _get_native_vtype(value[0] if type(value) == list else value)
    column = columns[value_types[vtype]['column_name']]
    op_method = value_comparison_methods[op]
    if type(value) == list:
        db_value = [v.id if vtype in ('s', 'blob') else v for v in value]
    else:
        db_value = value.id if vtype in ('s', 'blob') else value
    return getattr(column, op_method)(db_value)

class Comparison:

    def __init__(self, key, op, value):
        self.key = key
        self.op = op
        self.value = value

    def __bool__(self):
        """Ensure Comparison makes sense when used directly in boolean context
        (as opposed to using it to specify filters)"""
        if self.op == 'eq':
            return (hash(self.key) == hash(self.value))
        else:
            raise QDValueError("Unsupported use of Comparison")

    def api_value(self):
        return {
            'key': serialize(self.key),
            'op': self.op,
            'value': serialize(self.value),
        }