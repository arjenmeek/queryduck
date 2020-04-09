import base64
import datetime
import uuid

from collections import defaultdict


class Statement:

    def __init__(self, uuid_str=None, uuid_=None, id_=None):
        self.uuid = uuid.UUID(uuid_str) if uuid_ is None else uuid_
        self.id = id_
        self.attributes = defaultdict(list)

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
        return '<Statement id={} uuid={}>'.format(self.id, self.uuid)


class Blob:

    def __init__(self, sha256_str=None, sha256=None, id_=None):
        self.sha256 = base64.b64decode(sha256_str) if sha256 is None else sha256
        self.id = id_

    def encoded_sha256(self):
        r = None if self.sha256 is None else base64.b64encode(self.sha256).decode('utf-8')
        return r

    def __repr__(self):
        return '<Blob id={} sha256={}>'.format(self.id, None if self.sha256 is None else self.encoded_sha256())


class Value:

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

    comparison_methods = {
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

    def __init__(self, serialized=None, native=None, db_columns=None, db_row=None, db_entities=None):
        if serialized is not None:
            self.vtype, ser_v = serialized.split(':', 1)
            options = self.value_types[self.vtype]
            self.column_name = options['column_name']
            self.serializer = options['serializer']
            self.v = options['factory'](ser_v)
        elif native is not None:
            for vt, options in self.value_types.items():
                if options['type'] == type(native):
                    self.vtype = vt
                    self.column_name = options['column_name']
                    self.serializer = options['serializer']
                    self.v = native
                    break
        elif db_columns is not None and db_row is not None:
            for vtype, options in self.value_types.items():
                column = db_columns[options['column_name']]
                v = db_row[column]
                if v is None or vtype == 'none':
                    continue
                self.vtype = vtype
                self.column_name = options['column_name']
                self.serializer = options['serializer']
                if vtype == 's':
                    uuid_ = db_row[db_entities['s'].c.uuid]
                    self.v = Statement(uuid_=uuid_, id_=v)
                elif vtype == 'blob':
                    sha256 = db_row[db_entities['blob'].c.sha256]
                    self.v = Blob(sha256=sha256, id_=v)
                else:
                    self.v = v
                break

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
        op_method = self.comparison_methods[op]
        return getattr(column, op_method)(self.db_value())

    def serialize(self):
        return '{}:{}'.format(self.vtype, self.serializer(self.v))


class ValueList:

    comparison_methods = {
        'in': 'in_',
    }

    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return 'ValueList {}>'.format(self.values)

    def column_compare(self, op, columns):
        column = columns[self.values[0].column_name]
        op_method = self.comparison_methods[op]
        db_values = [v.db_value() for v in self.values]
        return getattr(column, op_method)(db_values)
