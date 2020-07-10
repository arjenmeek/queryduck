from .types import Statement


class Transaction:

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

        return statements

    def get_statement_attribute(self, statement, predicate):
        return [s.triple[2] for s in self.find(s=statement, p=predicate)]

    def show(self):
        for idx, row in enumerate(self.statements):
            print(idx, row, row.triple)
