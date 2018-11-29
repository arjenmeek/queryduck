import argparse

from uuid import uuid4, UUID

from crunchylib.exceptions import GeneralError
from crunchylib.utility import serialize_value, deserialize_value
from crunchylib.query import StatementFilter

from .api import StatementAPI
from .schema import Schema
from .repositories import StatementRepository


class CrunchyClient(object):
    """Main class for the CrunchyVicar client application."""

    def __init__(self, config):
        """Make the config available for use, and initialize the API wrapper."""
        self.config = config
        api = StatementAPI(self.config['api']['url'])
        self.statements = StatementRepository(api)
        self.schema = Schema(
            UUID(self.config['schema']['root_uuid']),
            self.statements,
            self.config['schema']['keys']
        )

    def run(self, *params):
        """Perform the action requested by the user with appropriate parameters."""
        parser = argparse.ArgumentParser(description="Communicate with a CrunchyVicar server.")
        subparsers = parser.add_subparsers(help='action to perform')

        # Generic parsers for re-use
        parser_multi = argparse.ArgumentParser(add_help=False)
        parser_multi.add_argument('-f', '--filter', action='append')
        parser_multi.add_argument('-j', '--join', action='append')
        parser_multi.add_argument('-l', '--limit', action='append', type=int)
        parser_multi.add_argument('-s', '--sort', action='append')

        parser_single = argparse.ArgumentParser(add_help=False)
        parser_single.add_argument('-u', '--uuid')

        parser_create = argparse.ArgumentParser(add_help=False)
        parser_create.add_argument('-s', '--subject')
        parser_create.add_argument('-p', '--predicate')
        parser_create.add_argument('-o', '--object')
        parser_create.add_argument('-u', '--uuid')

        # Command-specific subparsers
        parser_list = subparsers.add_parser('list', parents=[parser_multi])
        parser_list.set_defaults(func=self.action_list_statements)

        parser_get = subparsers.add_parser('get', parents=[parser_single])
        parser_get.set_defaults(func=self.action_get_statement)

        parser_new = subparsers.add_parser('new', parents=[parser_create])
        parser_new.set_defaults(func=self.action_new_statement)

        parser_delete = subparsers.add_parser('delete', parents=[parser_single])
        parser_delete.set_defaults(func=self.action_delete_statement)

        args = parser.parse_args(params)
        if not 'func' in args:
            print("Please specify a command, or -h for help")
        else:
            return args.func(args)

    def _resolve_reference(self, reference):
        if reference.startswith('schema:'):
            dummy, schema_reference = reference.split(':', 1)
            result = self.schema[schema_reference]
        else:
            result = deserialize_value(reference)
        return result

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

    def action_list_statements(self, args):
        """Retrieve multiple Statements."""
        processed_filters = self._process_filters(args.filter)
        statements = self.statements.find(filters=processed_filters, joins=args.join)
        for statement in statements:
            statement.show()

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
