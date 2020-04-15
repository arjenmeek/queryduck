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
            s.attribute_loader = self.get_statement_attribute
            s.triple = tuple(self.unique_deserialize(r) for r in info)

    def unique_deserialize(self, ref):
        """Ensures there is only ever one instance of the same Statement present"""
        s = deserialize(ref)
        if type(s) == Statement:
            if s.uuid not in self.statements:
                s.attribute_loader = self.get_statement_attribute
                self.statements[s.uuid] = s
            return self.statements[s.uuid]
        elif type(s) == Blob:
            if s.sha256 not in self.blobs:
                self.blobs[s.sha256] = s
            return self.blobs[s.sha256]
        else:
            return s

    def get(self, uuid_):
        if not uuid_ in self.statements:
            s = Statement(uuid_=uuid_)
            s.attribute_loader = self.get_statement_attribute
            self.statements[uuid_] = s
        return self.statements[uuid_]

    def find(self, subject=None, predicate=None, object_=None):
        statements = []
        for s in self.statements.values():
            if s.triple is not None and \
                    (subject is None or s.triple[0] == subject) and \
                    (predicate is None or s.triple[1] == predicate) and \
                    (object_ is None or s.triple[2] == object_):
                statements.append(s)
        return statements

    def get_statement_attribute(self, statement, predicate):
        return [s.triple[2] for s in self.find(subject=statement, predicate=predicate)]


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
