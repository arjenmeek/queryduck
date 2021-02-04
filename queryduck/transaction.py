from .collection import statement_generator, BaseCollection
from .types import Statement


class Transaction(BaseCollection):
    def __init__(self):
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
        current = self.first(s, p, o)
        if current is None:
            return self.add(s, p, o)
        else:
            return current

    def find(self, s=None, p=None, o=None):
        return statement_generator(self.statements, s, p, o)

    def get_statement_attribute(self, statement, predicate):
        return [s.triple[2] for s in self.find(s=statement, p=predicate)]

    def show(self):
        for idx, row in enumerate(self.statements):
            print(idx, row, row.triple)
