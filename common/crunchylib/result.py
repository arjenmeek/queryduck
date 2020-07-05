from .types import Statement, Blob, deserialize


class StatementSet:

    def __init__(self, statements=None):
        self.statements = {}
        self.blobs = {}
        if statements:
            self.add(statements)

    def add(self, statements):
        for ref, info in statements.items():
            s = self.unique_deserialize(ref)
            s.triple = tuple(self.unique_deserialize(r) for r in info)

    def unique_deserialize(self, ref):
        """Ensures there is only ever one instance of the same Statement present"""
        s = deserialize(ref)
        if type(s) == Statement:
            if s.uuid not in self.statements:
                self.statements[s.uuid] = s
            return self.statements[s.uuid]
        elif type(s) == Blob:
            if s.sha256 not in self.blobs:
                self.blobs[s.sha256] = s
            elif s.volume and not self.blobs[s.sha256].volume:
                self.blobs[s.sha256].volume = s.volume
                self.blobs[s.sha256].path = s.path
            return self.blobs[s.sha256]
        else:
            return s

    def get(self, uuid_):
        if not uuid_ in self.statements:
            s = Statement(uuid_=uuid_)
            self.statements[uuid_] = s
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

    def get_statement_attribute(self, statement, predicate):
        return [s.triple[2] for s in self.find(s=statement, p=predicate)]


class ResultSet:

    def __init__(self, references, sts):
        self.sts = sts
        self.result_uuids = [deserialize(r).uuid for r in references]

    def getall(self):
        statements = []
        for uuid_ in self.result_uuids:
            s = self.sts.get(uuid_)
            statements.append(s)
        return statements
