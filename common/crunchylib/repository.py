import weakref

from .bindings import Bindings
from .types import Statement, Blob, serialize, deserialize
from .result import Result
from .utility import transform_doc


class StatementRepository:

    def __init__(self, connection):
        self.connection = connection
        self.statement_map = weakref.WeakValueDictionary()
        self.blob_map = weakref.WeakValueDictionary()

    def export_statements(self):
        r = self.connection.get_statements()
        return r['statements']

    def import_statements(self, ser_statements):
        self.connection.create_statements(ser_statements)

    def unique_deserialize(self, ref):
        """Ensures there is only ever one instance of the same Statement present"""
        s = deserialize(ref)
        if type(s) == Statement:
            if s.uuid not in self.statement_map:
                self.statement_map[s.uuid] = s
            return self.statement_map[s.uuid]
        elif type(s) == Blob:
            if s.sha256 not in self.blob_map:
                self.blob_map[s.sha256] = s
            elif s.volume and not self.blobs[s.sha256].volume:
                self.blobs[s.sha256].volume = s.volume
                self.blobs[s.sha256].path = s.path
            return self.blobs[s.sha256]
        else:
            return s

    def bindings_from_schema(self, schema):
        bindings_content = {}
        for k, v in schema['bindings'].items():
            bindings_content[k] = self.unique_deserialize(v)
        bindings = Bindings(bindings_content)
        return bindings

    def query(self, *comparisons, query=None):
        filters = [c.api_value() for c in comparisons]
        if query:
            query = transform_doc(query, serialize)
        else:
            query = {}
            for f in filters:
                if not f['key'] in query:
                    query[f['key']] = {}
                query[f['key']]['_{}_'.format(f['op'])] = f['value']

            query = {k: v['_eq_'] if type(v) == dict and len(v) == 1
                and '_eq_' in v else v for k, v in query.items()}

        response = self.connection.query_statements(query)
        result = self._result_from_response(response)
        return result

    def _result_from_response(self, response):
        statements = {}
        for k, v in response['statements'].items():
            statement = self.unique_deserialize(k)
            if statement.triple is None:
                statement.triple = (
                    self.unique_deserialize(v[0]),
                    self.unique_deserialize(v[1]),
                    self.unique_deserialize(v[2]),
                )
            statements[statement.uuid] = statement

        values = []
        for ref in response['references']:
            value = self.unique_deserialize(ref)
            values.append(value)
        result = Result(statements=statements, values=values)
        return result

    def raw_create(self, ser_statements):
        return self.connection.create_statements(ser_statements)

    def submit(self, transaction):
        if len(transaction.statements) == 0:
            return None
        ser_statements = []
        for s in transaction.statements:
            ser_statements.append([None] + [v.id
                if type(v) == Statement and v.uuid is None
                else serialize(v) for v in s.triple])
        return self.connection.create_statements(ser_statements)
