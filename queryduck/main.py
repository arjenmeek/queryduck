import json
import os

from os.path import dirname, expanduser, join as pjoin

from .connection import Connection
from .constants import DEFAULT_SCHEMA_FILES
from .repository import StatementRepository


class QueryDuck:

    def __init__(self, url, username, password, extra_schema_files=None):
        self.main_dir = dirname(dirname(__file__))
        self.conn = Connection(url, username, password)
        self.repo = None
        self.bindings = None
        if extra_schema_files is not None:
            self.extra_schema_files = extra_schema_files
        else:
            self.extra_schema_files = []

    def get_repo(self):
        if self.repo is None:
            self.repo = StatementRepository(self.conn)
        return self.repo

    def get_bindings(self):
        if self.bindings is None:
            schemas = []
            for filename in DEFAULT_SCHEMA_FILES + self.extra_schema_files:
                if '/' in filename:
                    filepath = expanduser(filename)
                else:
                    filepath = pjoin(os.path.dirname(__file__), 'schemas',
                        filename)

                with open(filepath, 'r') as f:
                    schemas.append(json.load(f))

            repo = self.get_repo()
            self.bindings = repo.bindings_from_schemas(schemas)

        return self.bindings

