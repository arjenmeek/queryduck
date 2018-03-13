from crunchylib.utility import StatementReference

from .models import Statement


class StatementRepository(object):

    def __init__(self, api):
        self.api = api

    def save(self, statement):
        quad = statement.get_unresolved_quad()
        self.api.save_statement(quad)

    def delete(self, statement):
        self.api.delete_statement(statement.uuid)

    def resolve_reference(self, orig_value, context=None):
        """Resolve StatementReference instances into an actual Statement."""
        if isinstance(orig_value, StatementReference):
            value = orig_value.resolve(context, self)
        else:
            value = orig_value
        return value

    def load_statement(self, uuid_, subject, predicate, object_):
        statement = Statement(uuid_, subject, predicate, object_, statement_repository=self)
        return statement

    def get_by_uuid(self, uuid_):
        quad = self.api.get_statement(uuid_)
        statement = self.load_statement(*quad)
        return statement

    def find(self):
        quads = self.api.find_statements()
        statements = [self.load_statement(*q) for q in quads]
        return statements

