from .types import Statement, Blob, deserialize


class Result:

    def __init__(self, statements, values, files):
        self.statements = statements
        self.values = values
        self.files = files

    def get(self, uuid_):
        return self.statements[uuid_]

    def find(self, s=None, p=None, o=None):
        statements = []
        for st in self.statements.values():
            if st.triple is not None and \
                    (s is None or st.triple[0] == s) and \
                    (p is None or st.triple[1] == p) and \
                    (o is None or st.triple[2] == o):
                statements.append(st)
        return statements

    def first(self, s=None, p=None, o=None):
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
