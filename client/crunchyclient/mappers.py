import uuid

from crunchylib.utility import deserialize_value, serialize_value

from .models import Statement


class ResultSet(object):

    def __init__(self, statements, results, joins):
        self.statements = statements
        self.results = results
        self.joins = joins
        self.join_to_idx = {join: idx for idx, join in enumerate(self.joins)}

    def get_rows(self):
        rows = []
        for res in self.results:
            row = [self.statements[u] if u is not None else None for u in res]
            rows.append(row)
        return rows

    def get_rowdicts(self):
        rowdicts = []
        for res in self.results:
            rowdict = {}
            for j, i in self.join_to_idx.items():
                uuid_ = res[i]
                if uuid_ is not None:
                    rowdict[j] = self.statements[uuid_]
                else:
                    rowdict[j] = None
            rowdicts.append(rowdict)
        return rowdicts

    def get_column(self, colnr = 0):
        column_values = []
        for res in self.results:
            column_value = self.statements[res[colnr]]
            column_values.append(column_value)
        return column_values


class StatementMapper(object):
    """Maps between raw API objects/calls and Statement objects."""

    def __init__(self, api):
        self.api = api

    def _process_raw_statement(self, raw_statement):
        """Deserialize a set of raw values"""
        elements = [deserialize_value(v) for v in raw_statement]
        return elements

    def get_statement(self, uuid_):
        """Fetch a statement"""
        raw_statement = self.api.get_raw_statement(uuid_)
        statement = self._deserialize_statement(*raw_statement)
        return statement

    def get_by_uuid(self, uuid_):
        return self.get_statement(uuid_)

    def _serialize_statement(self, statement):
        quad = statement.get_unresolved_quad()
        raw_statement = [serialize_value(v) for v in quad]
        return raw_statement

    def _deserialize_statement(self, *element_strings):
        elements = [deserialize_value(v) for v in element_strings]
        statement = Statement(*elements, statement_repository=self)
        return statement

    def _process_results(self, raw_results, raw_statements, join_names):
        statements = {}
        for key, raw_statement in raw_statements.items():
            statement = self._deserialize_statement(*raw_statement)
            statements[statement.uuid] = statement

        results = []

        for raw_resultrow in raw_results:
            row = []
            for uuid_str in raw_resultrow:
                if uuid_str is not None:
                    row.append(uuid.UUID(uuid_str))
                else:
                    row.append(None)
            results.append(row)
        resultset = ResultSet(statements, results, join_names)
        return resultset

    def find_statements(self, filters=None, joins=None, multi=False):
        """Retrieve multiple statements"""
        params = {}
        filter_strings = join_strings = None
        join_names = ['main']
        if filters is not None:
            filter_strings = [f.serialize() for f in filters]
        if joins is not None:
            join_strings = [j.serialize() for j in joins]
            join_names += [j.name for j in joins]

        raw_results, raw_statements = self.api.find_raw_statements(filter_strings, join_strings)
        resultset = self._process_results(raw_results, raw_statements, join_names)
        return resultset

    def save_statement(self, statement):
        """Persist a statement"""
        raw_statement = self._serialize_statement(statement)
        self.api.save_raw_statement(statement.uuid, raw_statement)

    def delete_statement(self, uuid_):
        """Delete a statement"""
        self.api.delete_raw_statement(uuid_)
