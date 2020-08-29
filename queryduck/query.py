
class QueryElement:

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.value)


class MatchObject(QueryElement):

    prefix = '='

    @staticmethod
    def get_join_columns(v):
        return ('subject_id', 'object_statement_id')


class MatchSubject(QueryElement):

    prefix = '~'

    @staticmethod
    def get_join_columns(v):
        if v is None or type(v).__name__ == 'Blob':
            lhs_column = 'object_blob_id'
        else:
            lhs_column = 'object_statement_id'
        return (lhs_column, 'subject_id')


class MetaObject(QueryElement):

    prefix = '@'

    @staticmethod
    def get_join_columns(v):
        return ('subject_id', 'object_statement_id')


class MetaSubject(QueryElement):

    prefix = '&'


class Comparison(QueryElement):

    prefix = '_'


query_prefixes = {
    '=': MatchObject,
    '~': MatchSubject,
    '@': MetaObject,
    '&': MetaSubject,
    '_': Comparison,
}
