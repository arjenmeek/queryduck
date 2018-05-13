import argparse

from uuid import uuid4, UUID

from crunchylib.exceptions import GeneralError
from crunchylib.utility import serialize_value, deserialize_value

from .api import StatementAPI
from .repositories import StatementRepository


class CrunchyClient(object):
    """Main class for the CrunchyVicar client application."""

    def __init__(self, config):
        """Make the config available for use, and initialize the API wrapper."""
        self.config = config
        api = StatementAPI(self.config['api']['url'])
        self.statements = StatementRepository(api)

    def run(self, *params):
        """Perform the action requested by the user with appropriate parameters."""
        parser = argparse.ArgumentParser(description="Communicate with a CrunchyVicar server.")
        subparsers = parser.add_subparsers(help='action to perform')

        parser_multi = argparse.ArgumentParser(add_help=False)
        parser_multi.add_argument('-f', '--filter', action='append')
        parser_multi.add_argument('-j', '--join', action='append')
        parser_multi.add_argument('-l', '--limit', action='append', type=int)
        parser_multi.add_argument('-s', '--sort', action='append')

        parser_single = argparse.ArgumentParser(add_help=False)
        parser_single.add_argument('-u', '--uuid', action='append')

        parser_create = argparse.ArgumentParser(add_help=False)
        parser_create.add_argument('-s', '--subject')
        parser_create.add_argument('-p', '--predicate')
        parser_create.add_argument('-o', '--object')

        parser_list = subparsers.add_parser('list_statements', parents=[parser_multi])
        parser_list.set_defaults(func=self.action_list_statements)

        parser_get = subparsers.add_parser('get_statement', parents=[parser_single])
        parser_list.set_defaults(func=self.action_get_statement)

        parser_get = subparsers.add_parser('new_uuid_statement', parents=[parser_single])
        parser_list.set_defaults(func=self.action_new_uuid_statement)

        parser_get = subparsers.add_parser('delete_statement', parents=[parser_single])
        parser_list.set_defaults(func=self.action_delete_statement)

        args = parser.parse_args(params)
        return args.func(args)

    def action_list_statements(self, args):
        """Retrieve multiple Statements."""
        statements = self.statements.find(filters=args.filter, joins=args.join)
        for statement in statements:
            statement.show()

    def action_get_statement(self, args):
        """Get a single Statement by its UUID reference."""
        uuid_ = deserialize_value(args.uuid)
        statement = self.statements.get_by_uuid(uuid_)
        statement.show()

    def action_new_uuid_statement(self, args):
        """Create a new Statement with a specific UUID reference."""
        quad = [deserialize_value(v) for v in [args.uuid, args.subject, args.predicate, args.object]]
        statement = self.statements.load_statement(*quad)
        self.statements.save(statement)
        statement.show()

    def action_new_statement(self, args):
        """Create a new Statement with an auto-generated UUID reference."""
        uuid_ = uuid4()
        uuid_str = serialize_value(uuid_)
        return self.action_new_uuid_statement(uuid_str, args.subject, args.predicate, args.object)

    def action_delete_statement(self, args):
        """Delete a Statement by its UUID reference."""
        uuid_ = deserialize_value(args.uuid)
        statement = self.statements.get_by_uuid(uuid_)
        self.statements.delete(statement)
