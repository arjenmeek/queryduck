import datetime
import uuid

from collections import defaultdict

class Statement:

    def __init__(self, uuid_=None, id_=None):
        self.uuid = uuid_
        self.id = id_
        self.attributes = defaultdict(list)

    def __json__(self, request):
        data = {
            'uuid': 'uuid:{}'.format(self.uuid),
        }
        for k, vlist in self.attributes.items():
            data[k] = []
            for v in vlist:
                data[k].append(v.serialize())
        return data


class Value(object):

    value_types = {
        'int': {
            'factory': int,
            'column_name': 'object_integer',
            'serializer': str,
        },
        'bool': {
            'factory': bool,
            'column_name': 'object_boolean',
            'serializer': str,
        },
        'float': {
            'factory': float,
            'column_name': 'object_float',
            'serializer': str,
        },
        'str': {
            'factory': str,
            'column_name': 'object_string',
            'serializer': str,
        },
        'datetime': {
            'factory': lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%f'),
            'column_name': 'object_datetime',
            'serializer': lambda dt: dt.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        },
        'st': {
            'factory': Statement,
            'column_name': 'object_statement_id',
            'serializer': lambda st: st.uuid,
        },
        'none': {
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
            self.vtype, ser_content = serialized.split(':', 1)
            options = self.value_types[self.vtype]
            self.column_name = options['column_name']
            self.serializer = options['serializer']
            self.content = options['factory'](ser_content)
        elif db_columns is not None and db_row is not None:
            for vtype, options in self.value_types.items():
                column = db_columns[options['column_name']]
                content = db_row[column]
                if content is None or vtype == 'none':
                    continue
                self.vtype = vtype
                self.column_name = options['column_name']
                self.serializer = options['serializer']
                if vtype == 'st':
                    uuid_ = db_row[db_entities['st'].c.uuid]
                    self.content = Statement(uuid_=uuid_, id_=content)
                else:
                    self.content = content
                break


    def db_value(self):
        if self.vtype == 'st':
            return self.content.id
        else:
            return self.content

    def column_compare(self, op, columns):
        column = columns[self.column_name]
        op_method = self.comparison_methods[op]
        return getattr(column, op_method)(self.db_value())

    def serialize(self):
        return '{}:{}'.format(self.vtype, self.serializer(self.content))
