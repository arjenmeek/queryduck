from .result import StatementSet
from .types import Statement, serialize, deserialize, Placeholder
from .utility import transform_doc


class Transaction:

    def __init__(self, repository):
        self.repository = repository
        self.statements = []

    def add(self, s, p, o):
        st = Statement(id_=len(self.statements))
        st.triple = (
            s if s is not None else st,
            p if p is not None else st,
            o if o is not None else st,
        )
        self.statements.append(st)
        return st

    def ensure(self, s, p, o):
        current = self.find(s, p, o)
        if len(current) == 0:
            return self.add(s, p, o)
        else:
            return current[0]

    def find(self, s=None, p=None, o=None):
        statements = []
        for st in self.statements:
            if st.triple is not None and \
                    (s is None or st.triple[0] == s) and \
                    (p is None or st.triple[1] == p) and \
                    (o is None or st.triple[2] == o):
                statements.append(st)
        if s.uuid and p.uuid and (type(o) != Statement or o.uuid):
            statements += self.repository.sts.find(s, p, o)
        else:
            print("NOPE", s, p, o)

        return statements

    def show(self):
        for idx, row in enumerate(self.statements):
            print(idx, row, row.triple)


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

    def submit(self, transaction):
        if len(transaction.statements) == 0:
            return None
        ser_statements = []
        for s in transaction.statements:
            ser_statements.append([v.id
                if type(v) == Statement and v.uuid is None
                else serialize(v) for v in s.triple])
        return self.api.create_statements(ser_statements)

    def load_schema(self, root_uuid, keys):
        schema_simple = self.api.establish_schema(root_uuid, keys)
        schema = {}
        for k, v in schema_simple.items():
            schema[k] = self.sts.unique_deserialize(v)
        return schema

    def transaction(self):
        return Transaction(self)
