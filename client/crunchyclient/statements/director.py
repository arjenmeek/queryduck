import argparse
import datetime

from collections import OrderedDict
from uuid import uuid4, UUID

from crunchylib.exceptions import GeneralError
from crunchylib.utility import serialize_value, deserialize_value
from crunchylib.query import StatementJoin, StatementFilter

from .mappers import StatementMapper
from .schema import Schema
from .repositories import StatementRepository


class StatementDirector(object):

    def __init__(self, master):
        self.master = master
        self.api = self.master.api
        mapper = StatementMapper(self.api)
        self.statements = StatementRepository(mapper)
        self.schema = Schema(
            UUID(self.master.config['schema']['root_uuid']),
            self.statements,
            self.master.config['schema']['keys']
        )

        parser_do = argparse.ArgumentParser(add_help=False)
        parser_do.add_argument('what', nargs='+')

        parser_multi = argparse.ArgumentParser(add_help=False)
        parser_multi.add_argument('-f', '--filter', action='append')
        parser_multi.add_argument('-j', '--join', action='append')
        parser_multi.add_argument('-l', '--limit', action='append', type=int)
        parser_multi.add_argument('-s', '--sort', action='append')
        parser_multi.add_argument('-c', '--column', action='append')

        parser_single = argparse.ArgumentParser(add_help=False)
        parser_single.add_argument('-u', '--uuid')

        parser_create = argparse.ArgumentParser(add_help=False)
        parser_create.add_argument('-s', '--subject')
        parser_create.add_argument('-p', '--predicate')
        parser_create.add_argument('-o', '--object')
        parser_create.add_argument('-u', '--uuid')

        self.master.register_command_parser('do', parser_do, self.action_do)
        self.master.register_command_parser('list', parser_multi, self.action_list_statements)
        self.master.register_command_parser('get', parser_single, self.action_get_statement)
        self.master.register_command_parser('new', parser_create, self.action_new_statement)
        self.master.register_command_parser('delete', parser_single, self.action_delete_statement)

    def _simple_resolve_reference(self, reference):
        if reference.startswith('@'):
            schema_reference = reference[1:]
            result = serialize_value(self.schema[schema_reference])
        elif reference.startswith('$'):
            label_reference = reference[1:]
            result = self._get_by_label(label_reference)
        else:
            result = reference
        return result

    def _resolve_reference(self, reference):
        if reference.startswith('schema/'):
            dummy, schema_reference = reference.split('/', 1)
            result = self.schema[schema_reference]
        elif reference.startswith('@'):
            dummy, label_reference = reference.split('/', 1)
            result = self.schema[schema_reference]
        else:
            result = deserialize_value(reference)
        return result

    def _process_joins(self, joins):
        processed_joins = []
        for j in joins:
            parts = j.split(',')
            name = parts[0]
            lhs = self._resolve_reference(parts[1])
            operand = parts[2]
            if len(parts) == 4:
                rhs = self._resolve_reference(parts[3])
            else:
                rhs = None
            sj = StatementJoin(name, lhs, operand, rhs)
            processed_joins.append(sj)
        return processed_joins

    def _process_filters(self, filters):
        processed_filters = []
        for f in filters:
            parts = f.split(',')
            lhs = self._resolve_reference(parts[0])
            operand = parts[1]
            if len(parts) == 3:
                rhs = self._resolve_reference(parts[2])
            else:
                rhs = None
            sf = StatementFilter(lhs, operand, rhs)
            processed_filters.append(sf)
        return processed_filters

    def _show_statement_rowdict(self, statement_rowdict, columns):
        statement_str = ''
        for column in columns:
            if '.' in column:
                join_name, attribute_name = column.split('.', 1)
                statement = statement_rowdict[join_name]
                prefixed_attribute_name = '_' + attribute_name
                if statement is not None:
                    readable_value = self._readable_value(getattr(statement, prefixed_attribute_name), statement)
                else:
                    readable_value = '--- NONE ---'
            else:
                join_name = column
                statement = statement_rowdict[join_name]
                readable_value = self._readable_value(statement)

            statement_str += "{: <20} ".format(readable_value)
        print(statement_str)

    def _readable_value(self, value, context = None):
        if value is None:
            return '--- NONE ---'
        elif type(value) == UUID:
            return str(value)
        elif type(value) == int:
            return str(value)
        elif type(value) == str:
            return '"{}"'.format(value)
#        elif type(value) == datetime.datetime:
#            return 'datetime:{}'.format(datetime.datetime.strftime(value, '%Y-%m-%dT%H:%M:%S.%f'))
#        elif type(value) == SelfReference:
#            return 'special:self'
#        elif type(value) == ColumnReference:
#            return '[{}.{}]'.format(value.alias, value.column)
        elif hasattr(value, 'is_statement') and value.is_statement:
            if context is not None and value.uuid == context.uuid:
                return "*self*"
            schema_name = self.schema.find_name(value)
            if schema_name:
                return 'schema:{}'.format(schema_name)
            else:
                return 'st:{}...'.format(str(value.uuid)[0:12])
        elif hasattr(value, 'is_blob') and value.is_blob:
            return 'blob:{}'.format(value.get_identifier())

    def action_list_statements(self, args):
        """Retrieve multiple Statements."""
        processed_filters = processed_joins = None
        if args.join is not None:
            processed_joins = self._process_joins(args.join)
        if args.filter is not None:
            processed_filters = self._process_filters(args.filter)
        if args.column is not None:
            columns = args.column
        else:
            columns = ['main', 'main.subject', 'main.predicate', 'main.object']
        resultset = self.statements.find(filters=processed_filters, joins=processed_joins, multi=True)

        header = ''
        separator = ''
        for column in columns:
            header += "{: <20} ".format(column)
            separator += "{: <20} ".format('-' * len(column))
        print(header)
        print(separator)

        for rowdict in resultset.get_rowdicts():
            self._show_statement_rowdict(rowdict, columns)

    def action_get_statement(self, args):
        """Get a single Statement by its UUID reference."""
        uuid_ = deserialize_value(args.uuid)
        statement = self.statements.get_by_uuid(uuid_)
        statement.show()

    def action_new_statement(self, args):
        """Create a new Statement."""
        if 'uuid' in args and args.uuid is not None:
            uuid_str = args.uuid
        else:
            uuid_ = uuid4()
            uuid_str = serialize_value(uuid_)
        quad = [self._resolve_reference(v) for v in [uuid_str, args.subject, args.predicate, args.object]]
        statement = self.statements.load_statement(*quad)
        self.statements.save(statement)
        statement.show()

    def action_delete_statement(self, args):
        """Delete a Statement by its UUID reference."""
        uuid_ = deserialize_value(args.uuid)
        statement = self.statements.get_by_uuid(uuid_)
        self.statements.delete(statement)

    def action_do(self, args):
        line = ' '.join(args.what)
        if ' ' in line:
            command, options = line.split(' ', 1)
        else:
            command = line
        if command == 'create':
            statements = []
            statement_strs = options.split('|')
            for sts in statement_strs:
                parts = []
                for part in sts.split(' '):
                    if part == '0':
                        parts.append(0)
                    else:
                        parts.append(self._simple_resolve_reference(part))
                print("creating s = {}, p = {}, o = {}".format(*parts))
                statements.append(parts)
            self.api.create_statements(statements)
        elif command == 'query':
            query = self._parse_query_string(options)
            for row in self.api.query_statements(query):
                for key, quad in row.items():
                    if quad is None:
                        print('  {}: None'.format(key))
                    else:
                        print('  {}'.format(key), quad)
                        #for v in quad:
                        #    print('    {}'.format(v))
                print('---')


    def _parse_query_string(self, query_string):
        q = OrderedDict()
        cur_key = None
        cur_values = []
        cur_quote = None
        last_key = None

        state = 'base'
        op = None

        for i, c in enumerate(query_string + ' '):
            if state == 'base':
                if c == ' ':
                    continue
                elif c == '+':
                    state = 'key'
                    current = ''
                    op = 'c'
                elif c == '=':
                    state = 'key'
                    current = ''
                    op = 'f'
                else:
                    state = 'key'
                    current = c
                    op = 'j'
            elif state == 'key':
                if c == ':':
                    cur_key = current
                    state = 'value'
                    current = ''
                else:
                    current += c
            elif state == 'value':
                if c == '.':
                    cur_values.append(self._simple_resolve_reference(current))
                    current = ''
                elif c == ' ':
                    cur_values.append(self._simple_resolve_reference(current))
                    key = op + '_' + cur_key
                    if not key in q:
                        q[key] = []
                    q[key].append('.'.join(cur_values))
                    current = None
                    cur_key = None
                    cur_values = []
                    state = 'base'
                elif c in ['"', "'"]:
                    state = 'quoted'
                    cur_quote = c
                else:
                    current += c
            elif state == 'quoted':
                if c == cur_quote:
                    state = 'value'
                    cur_quote = None
                else:
                    current += c

        return q
