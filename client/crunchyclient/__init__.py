import argparse

from .api import CrunchyAPI
from .statements.director import StatementDirector
from .storage.director import StorageDirector


class CrunchyClient(object):
    """Main class for the CrunchyVicar client application."""

    def __init__(self, config):
        """Make the config available for use, and initialize the API wrapper."""
        self.config = config
        self.parsers = {}
        self.api = CrunchyAPI(self.config['api']['url'])
        self._parser = argparse.ArgumentParser(description="Communicate with a CrunchyVicar server.")
        self._subparsers = self._parser.add_subparsers(help='action to perform')

        statement_director = StatementDirector(self)
        storage_director = StorageDirector(self)

    def register_command_parser(self, command, parent, func):
        self.parsers[command] = self._subparsers.add_parser(command, parents=[parent])
        self.parsers[command].set_defaults(func=func)

    def run(self, *params):
        """Perform the action requested by the user with appropriate parameters."""
        args = self._parser.parse_args(params)
        if not 'func' in args:
            print("Please specify a command, or -h for help")
        else:
            return args.func(args)
