import uuid

from .exceptions import QDSchemaError
from .types import serialize

class Schema:

    def __init__(self, content):
        self._content = content

    def __getitem__(self, attr):
        if not attr in self._content:
            raise QDSchemaError(
                "Key is not part of this Schema: {}".format(attr))
        return self._content[attr]

    def __getattr__(self, attr):
        return self._content[attr]

    def reverse(self, statement):
        for k, v in self._content.items():
            if v == statement:
                return k
        else:
            return None

class SchemaProcessor:

    def fill_prototype(self, prototype):
        schema = {}
        for pk, pv in prototype.items():
            if pk == 'bindings':
                schema['bindings'] = {}
                for k, v in prototype['bindings'].items():
                    schema['bindings'][k] = \
                        's:{}'.format(uuid.uuid4()) if v is None else v
            elif pk == 'statements':
                schema['statements'] = []
                for s in prototype['statements']:
                    schema['statements'].append(['s:{}'.format(uuid.uuid4())
                        if e is None else e for e in s])
            else:
                schema[pk] = pv
        return schema

    def statements_from_schema(self, bindings, schema):
        statements = []
        for prototype in schema['statements']:
            statement = [v if ':' in v else serialize(bindings[v])
                for v in prototype]
            statements.append(statement)
        return statements

class Bindings:

    def __init__(self, content):
        self._content = content

    def __getitem__(self, attr):
        if not attr in self._content:
            raise QDSchemaError(
                "Key is not part of these Bindings: {}".format(attr))
        return self._content[attr]

    def __getattr__(self, attr):
        return self._content[attr]

    def reverse_exists(self, statement):
        for k, v in self._content.items():
            if v == statement:
                return True
        else:
            return False

    def reverse(self, statement):
        for k, v in self._content.items():
            if v == statement:
                return k
        else:
            return statement
