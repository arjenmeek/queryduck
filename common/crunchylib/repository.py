from .result import StatementSet
from .value import serialize, deserialize


class StatementRepository:

    def __init__(self, api):
        self.api = api
        self.sts = StatementSet()

    def query(self, *filter_specs):
        filters = []
        for fs in filter_specs:
            filters.append({'key': serialize(fs['key']),
                'value': serialize(fs['value'])})

        r = self.api.query_statements(filters)
        self.sts.add(r['statements'])
        return [self.sts.get(deserialize(ref).uuid) for ref in r['references']]

    def load_schema(self, root_uuid, keys):
        schema_simple = self.api.establish_schema(root_uuid, keys)
        schema = {}
        for k, v in schema_simple.items():
            schema[k] = self.sts.unique_deserialize(v)
        return schema
