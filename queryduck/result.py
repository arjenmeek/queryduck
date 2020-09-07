from collections import defaultdict

from .types import Statement, Blob
from .serialization import deserialize


class Result:

    def __init__(self, statements, values, files, more):
        self.statements = statements
        self.values = values
        self.files = files
        self.more = more
        self.indexed = None

    def index(self):
        self.indexed = defaultdict(list)
        for st in self.statements.values():
            for triple in [
                (st.triple[0], st.triple[1], st.triple[2]),
                (None,         st.triple[1], st.triple[2]),
                (st.triple[0], None,         st.triple[2]),
                (st.triple[0], st.triple[1], None,       ),
                (None,         None,         st.triple[2]),
                (None,         st.triple[1], None,       ),
                (st.triple[0], None,         None,       ),
            ]:
                self.indexed[triple].append(st)

    def get(self, uuid_):
        return self.statements[uuid_]

    def find(self, s=None, p=None, o=None):
        if self.indexed:
            return self.indexed[(s, p, o)]
        statements = []
        for st in self.statements.values():
            if st.triple is not None and \
                    (s is None or st.triple[0] == s) and \
                    (p is None or st.triple[1] == p) and \
                    (o is None or st.triple[2] == o):
                statements.append(st)
        return statements

    def first(self, s=None, p=None, o=None):
        if self.indexed:
            k = (s, p, o)
            return self.indexed[k][0] if k in self.indexed else None
        statements = []
        for st in self.statements.values():
            if st.triple is not None and \
                    (s is None or st.triple[0] == s) and \
                    (p is None or st.triple[1] == p) and \
                    (o is None or st.triple[2] == o):
                return st
        return None

    def objects_for(self, subject, predicate):
        return [s.triple[2] for s in self.find(s=subject, p=predicate)]

    def object_for(self, subject, predicate):
        st = self.first(s=subject, p=predicate)
        return None if st is None else st.triple[2]

    def subjects_for(self, object_, predicate):
        return [s.triple[0] for s in self.find(p=predicate, o=object_)]

    def subject_for(self, object_, predicate):
        st = self.first(p=predicate, o=object_)
        return None if st is None else st.triple[0]
