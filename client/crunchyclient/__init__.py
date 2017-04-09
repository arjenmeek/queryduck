from uuid import uuid4, UUID

from crunchylib.exceptions import GeneralError
from crunchylib.utility import deserialize_value

from .api import StatementAPI
from .repositories import StatementRepository


class CrunchyClient(object):
    """Main class for the CrunchyVicar client application."""

    def __init__(self, config):
        """Make the config available for use, and initialize the API wrapper."""
        self.config = config
        api = StatementAPI(self.config['api']['url'])
        self.statements = StatementRepository(api)

    def run(self, action, *params):
        """Perform the action requested by the user with appropriate parameters."""
        func_name = 'action_{}'.format(action)
        if hasattr(self, func_name):
            func = getattr(self, func_name)
        else:
            raise GeneralError("No such action: {}".format(action))

        return func(*params)

    def action_list_statements(self):
        """Retrieve multiple Statements."""
        statements = self.statements.find()
        for statement in statements:
            statement.show()

    def action_get_statement(self, uuid_str):
        """Get a single Statement by its UUID reference."""
        uuid_ = deserialize_value(uuid_str)
        statement = self.statements.get_by_uuid(uuid_)
        statement.show()

    def action_new_uuid_statement(self, uuid_str, subject_str, predicate_str, object_str):
        """Create a new Statement with a specific UUID reference."""
        statement = [uuid_str, subject_str, predicate_str, object_str]
        self.api.put('statements/{}'.format(uuid_str), statement)

    def action_new_statement(self, subject_str, predicate_str, object_str):
        """Create a new Statement with an auto-generated UUID reference."""
        uuid_ = uuid4()
        uuid_str = 'uuid:{}'.format(uuid_)
        statement = [uuid_str, subject_str, predicate_str, object_str]
        self.api.put('statements/{}'.format(uuid_str), statement)
