import base64
import datetime
import uuid

from collections import defaultdict
from decimal import Decimal

from .exceptions import QDValueError


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
