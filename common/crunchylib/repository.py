from .result import StatementSet
from .types import serialize, deserialize, Placeholder
from .utility import transform_doc


class NewStatementList:

    def __init__(self):
        self.statements = []

    def add(self, s, p, o):
        pl = Placeholder(len(self.statements))
        self.statements.append((
            s if s is not None else pl,
            p if p is not None else pl,
            o if o is not None else pl,
        ))
        return pl

    def show(self):
        for idx, row in enumerate(self.statements):
            print(idx, row)

class StatementRepository:

    def __init__(self, api):
        self.api = api
        self.sts = StatementSet()

    def get(self, reference):
        r = self.api.get_statement(reference)
        self.sts.add(r['statements'])
        return self.sts.unique_deserialize(r['reference'])

    def export_statements(self):
        r = self.api.get_statements()
        return r['statements']

    def import_statements(self, ser_statements):
        self.api.create_statements(ser_statements)

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

        r = self.api.query_statements(query)
        self.sts.add(r['statements'])
        return [self.sts.unique_deserialize(ref) for ref in r['references']]

    def create(self, statementlist):
        if len(statementlist.statements) == 0:
            return None
        ser_statements = []
        for s in statementlist.statements:
            ser_statements.append([v.id if type(v) == Placeholder
                else serialize(v) for v in s])
        self.api.create_statements(ser_statements)

    def load_schema(self, root_uuid, keys):
        schema_simple = self.api.establish_schema(root_uuid, keys)
        schema = {}
        for k, v in schema_simple.items():
            schema[k] = self.sts.unique_deserialize(v)
        return schema
