from .result import StatementSet
from .types import serialize, deserialize, Placeholder


class NewStatementList:

    def __init__(self):
        self.statements = []

    def add(self, s, p, o):
        self.statements.append((s, p, o))
        p = Placeholder(len(self.statements) - 1)


class StatementRepository:

    def __init__(self, api):
        self.api = api
        self.sts = StatementSet()

    def get(self, reference):
        r = self.api.get_statement(reference)
        self.sts.add(r['statements'])
        return self.sts.unique_deserialize(r['reference'])

    def query(self, *comparisons):
        filters = [c.api_value() for c in comparisons]

        r = self.api.query_statements(filters)
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
