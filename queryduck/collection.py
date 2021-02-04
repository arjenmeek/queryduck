from collections import defaultdict

def statement_generator(statements, s, p, o):
    for st in statements:
        if (
            st.triple is not None
            and (s is None or st.triple[0] == s)
            and (p is None or st.triple[1] == p)
            and (o is None or st.triple[2] == o)
        ):
            yield st

def grouped_statement_generator(collections, s, p, o):
    for coll in collections:
        for st in coll.find(s, p, o):
            yield st


class BaseCollection:

    def first(self, s=None, p=None, o=None):
        statements = self.find(s, p, o)
        return next(statements, None)

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
                (st.triple[0], st.triple[1],  None),
                (None, None, st.triple[2]),
                (None, st.triple[1], None),
                (st.triple[0], None, None),
            ]:
                self.indexed[triple].append(st)

    def get(self, uuid_):
        return self.statements[uuid_]

    def find(self, s=None, p=None, o=None):
        if self.indexed:
            return self.indexed[(s, p, o)]
        else:
            st_gen = statement_generator(self.statements.values(), s, p, o)
            return st_gen

    def get_files(self, blob):
        return self.files.get(blob, [])


class GroupedCollection(BaseCollection):
    def __init__(self, collections=None):
        self.collections = collections if collections is not None else []

    def add_collection(self, collection):
        self.collections.append(collection)

    def find(self, s=None, p=None, o=None):
        return grouped_statement_generator(self.collections, s, p, o)

    def get_files(self, blob):
        files = []
        for c in self.collections:
            files += c.get_files(blob)
        return files
