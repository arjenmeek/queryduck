import json
import os

from os.path import dirname, join as pjoin

from .connection import Connection
from .constants import DEFAULT_SCHEMA_FILES
from .repository import StatementRepository

class QueryDuck:

    def __init__(self, url, username, password):
        self.main_dir = dirname(dirname(__file__))
        self.conn = Connection(url, username, password)
        self.repo = None
        self.bindings = None

    def get_repo(self):
        if self.repo is None:
            self.repo = StatementRepository(self.conn)
        return self.repo

    def get_bindings(self):
        if self.bindings is None:
            schemas = []
            for filename in DEFAULT_SCHEMA_FILES:
                filepath = pjoin(self.main_dir, 'schemas', filename)
                with open(filepath, 'r') as f:
                    schemas.append(json.load(f))
            repo = self.get_repo()
            self.bindings = repo.bindings_from_schemas(schemas)
        return self.bindings

