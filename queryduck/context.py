from .collection import grouped_statement_generator, BaseCollection, GroupedCollection
from .query import Main, QDQuery
from .transaction import Transaction
from .types import Statement

class Context(BaseCollection):
    def __init__(self, repo, bindings, coll=None, transaction=None):
        self.repo = repo
        self.bindings = bindings
        self.coll = GroupedCollection()
        if coll:
            self.coll.add_collection(coll)
        self.transaction = transaction if transaction else Transaction()

    def get_bc(self):
        return self.bindings, self.coll

    def execute(self, query):
        result, collection = self.repo.execute(query)
        self.coll.add_collection(collection)
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

    def find(self, s=None, p=None, o=None):
        return grouped_statement_generator(self.coll.collections + [self.transaction], s, p, o)

    def get_files(self, blob):
        files = []
        for c in self.collections:
            files += c.get_files(blob)
        return files
