from .transaction import Transaction

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

    def ensure(self, s, p, o):
        current = self.coll.first(s, p, o)
        if current:
            return None
        return self.transaction.ensure(s, p, o)
