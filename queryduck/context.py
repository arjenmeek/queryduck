from .query import Main, QDQuery
from .transaction import Transaction
from .types import Statement

class Context:
    def __init__(self, repo, bindings, coll=None, transaction=None):
        self.repo = repo
        self.bindings = bindings
        self.coll = coll
        self.transaction = transaction if transaction else Transaction()

    def get_bc(self):
        return self.bindings, self.coll

    def execute(self, query):
        result, self.coll = self.repo.execute(query)
        return result

    def add(self, s, p, o):
        return self.transaction.add(s, p, o)

    def ensure(self, s, p, o):
        current = self.coll.first(s, p, o)
        if current:
            return None
        return self.transaction.ensure(s, p, o)

    def submit(self):
        self.repo.submit(self.transaction)

    def parse_identifier(self, identifier):
        if ":" in identifier:
            v = self.repo.unique_deserialize(identifier)
        elif identifier in self.bindings:
            v = self.bindings[identifier]
        elif identifier.startswith("/"):
            dummy, *resources, label = identifier.split("/")
            m = Main(Statement)
            q = QDQuery(Statement).add(
                m.object_for(self.bindings.label)==label,
                m.object_for(self.bindings.type)==self.bindings[resources[0]],
            )
            result, coll = self.repo.execute(q)
            v = label
        else:
            v = identifier

    def deserialize(self, string):
        if string.startswith("@") and string[1:] in self.bindings:
            return self.bindings[string[1:]]
        else:
            return self.repo.unique_deserialize(string)
