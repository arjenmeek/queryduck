import uuid

from crunchylib.utility import deserialize_value, serialize_value, StatementReference, ColumnReference
from crunchylib.query import StatementFilter

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

    def create_statement(self, uuid_, subject, predicate, object_):
        statement = self.load_statement(uuid_, subject, predicate, object_)
        self.save(statement)
        return statement

    def ensure_statement(self, subject, predicate, object_):
        filters = [
            StatementFilter(ColumnReference('main', 'subject'), 'eq', subject),
            StatementFilter(ColumnReference('main', 'predicate'), 'eq', predicate),
            StatementFilter(ColumnReference('main', 'object'), 'eq', object_),
        ]
        statements = self.find(filters=filters)
        if len(statements) >= 1:
            return statements[0]
#        else:
#            return self.create_statement(uuid.uuid4(), subject, predicate, object_)

    def find_by_attributes(self, subject=None, predicate=None, object_=None):
        filters = []
        if subject is not None:
            filters.append(StatementFilter(ColumnReference('main', 'subject'), 'eq', subject))
        if predicate is not None:
            filters.append(StatementFilter(ColumnReference('main', 'predicate'), 'eq', predicate))
        if object_ is not None:
            filters.append(StatementFilter(ColumnReference('main', 'object'), 'eq', object_))

        statements = self.find(filters=filters)
        return statements

    def get_by_uuid(self, uuid_):
        quad = self.api.get_statement(uuid_)
        statement = self.load_statement(*quad)
        return statement

    def find(self, filters=None, joins=None):
        quads = self.api.find_statements(filters=filters, joins=joins)
        statements = [self.load_statement(*q) for q in quads]
        return statements

