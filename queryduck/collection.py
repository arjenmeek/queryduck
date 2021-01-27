from collections import defaultdict

class BaseCollection:

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


class Collection(BaseCollection):
    def __init__(self, statements=None, files=None):
        self.statements = {}
        self.files = {}
        self.indexed = None
        if statements is not None:
            self.add_statements(statements)
        if files is not None:
            self.add_files(files)

    def add_statements(self, statements):
        if len(self.statements) == 0:
            self.statements = statements
        else:
            for k, v in statements.items():
                self.statements[k] = v
        self.index()

    def add_files(self, files):
        if len(self.files) == 0:
            self.files = files
        else:
            for k, v in files.items():
                self.files[k] = v

    def index(self):
        self.indexed = defaultdict(list)
        for st in self.statements.values():
            for triple in [
                (st.triple[0], st.triple[1], st.triple[2]),
                (None, st.triple[1], st.triple[2]),
                (st.triple[0], None, st.triple[2]),
                (
                    st.triple[0],
                    st.triple[1],
                    None,
                ),
                (None, None, st.triple[2]),
                (
                    None,
                    st.triple[1],
                    None,
                ),
                (
                    st.triple[0],
                    None,
                    None,
                ),
            ]:
                self.indexed[triple].append(st)

    def get(self, uuid_):
        return self.statements[uuid_]

    def find(self, s=None, p=None, o=None):
        if self.indexed:
            return self.indexed[(s, p, o)]
        statements = []
        for st in self.statements.values():
            if (
                st.triple is not None
                and (s is None or st.triple[0] == s)
                and (p is None or st.triple[1] == p)
                and (o is None or st.triple[2] == o)
            ):
                statements.append(st)
        return statements

    def first(self, s=None, p=None, o=None):
        if self.indexed:
            k = (s, p, o)
            return self.indexed[k][0] if k in self.indexed else None
        statements = []
        for st in self.statements.values():
            if (
                st.triple is not None
                and (s is None or st.triple[0] == s)
                and (p is None or st.triple[1] == p)
                and (o is None or st.triple[2] == o)
            ):
                return st
        return None

    def get_files(self, blob):
        return self.files.get(blob, [])


class GroupedCollection(BaseCollection):
    def __init__(self, collections=None):
        if collections:
            self.collections = collections
        else:
            self.collections = []

    def add_collection(self, collection):
        self.collections.append(collection)

    def find(self, s=None, p=None, o=None):
        statements = []
        for c in self.collections:
            statements += c.find(s, p, o)
        return statements

    def first(self, s=None, p=None, o=None):
        for c in self.collections:
            st = c.first(s, p, o)
            if st:
                return st
        return None

    def get_files(self, blob):
        files = []
        for c in self.collections:
            files += c.get_files(blob)
        return files
