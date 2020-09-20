
class QueryElement:

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.value)

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.value)


class MatchObject(QueryElement):

    prefix = '='

    @staticmethod
    def get_join_columns(v, t):
        return ('subject_id', 'object_statement_id')


class MatchSubject(QueryElement):

    prefix = '~'

    @staticmethod
    def get_join_columns(v, t):
        if v is None or type(v).__name__ == 'Blob' or t.name == 'blob':
            lhs_column = 'object_blob_id'
        else:
            lhs_column = 'object_statement_id'
        return (lhs_column, 'subject_id')


class MetaObject(QueryElement):

    prefix = '@'

    @staticmethod
    def get_join_columns(v, t):
        return ('subject_id', 'object_statement_id')


class MetaSubject(QueryElement):

    prefix = '&'


class FetchObject(QueryElement):

    prefix = '+'


class FetchSubject(QueryElement):

    prefix = '-'


class Comparison(QueryElement):

    prefix = '_'


query_prefixes = {
    '=': MatchObject,
    '~': MatchSubject,
    '@': MetaObject,
    '&': MetaSubject,
    '_': Comparison,
    '+': FetchObject,
    '-': FetchSubject,
}
