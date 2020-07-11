from .exceptions import CVSchemaError

class Schema:

    def __init__(self, content):
        self._content = content

    def __getitem__(self, attr):
        if not attr in self._content:
            raise CVSchemaError(
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
        pass # TODO

    def statements_from_schema(self, schema):
        statements = []
        for prototype in schema['statements']:
            statement = [v if ':' in v else schema['bindings'][v]
                for v in prototype]
            statements.append(statement)
        return statements
