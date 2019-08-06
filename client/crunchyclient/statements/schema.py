import uuid

from crunchylib.exceptions import NotFoundError
from crunchylib.utility import deserialize_value, serialize_value, SelfReference


class Schema(object):

    schema_keys = [
        'timestamp',
        'Resource',
        'Work',
        'Representation',
        'type',
        'content',
        'file_extension',
        'mime_major',
        'mime_minor',
        'mime_ext',
        'label',
    ]

    def __init__(self, root_uuid, statements, keys):
        self.root_uuid = root_uuid
        self.statements = statements
        self.keys = keys
        self.schema_statements = {}
        self.load_schema()
#        self.root_statement = self.ensure_uuid_statement(self.schema_root_uuid)
#        self.fill_schema_statements()
#        self.update_schema_statements()
#        self.label_schema_statements()

    def __getitem__(self, key):
        return self.schema_statements[key]

    def load_schema(self):
        try:
            self.root_statement = self.statements.get_by_uuid(self.root_uuid)
        except NotFoundError:
            self.root_statement = self.statements.create_statement(
                self.root_uuid,
                SelfReference(),
                SelfReference(),
                SelfReference()
            )
        key_statements = self.statements.find_by_attributes(predicate=self.root_statement)
        for st in key_statements:
            if type(st.object) == str:
                self.schema_statements[st.object] = st
        for key in self.keys:
            if not key in self.schema_statements:
                self.schema_statements[key] = self.statements.create_statement(
                    uuid.uuid4(),
                    SelfReference(),
                    self.root_statement,
                    key
                )
#        print('SCHEMA:', self.schema_statements)

    def ensure_uuid_statement(self, uuid_):
        statement = self.sts.get(uuid_)
        if not statement:
            statement = Statement(SelfStatement, SelfStatement, SelfStatement, force_uuid=self.schema_root_uuid)
            statement = self.sts.save(statement)
        return statement

    def fill_schema_statements(self):
        filters = [
            'main.predicate,eq,{}'.format(self.root_statement.reference()),
        ]
        predicate_statements = self.sts.find(filters=filters)
        self.schema_statements = {}
        for st in predicate_statements:
            if st.uuid != self.root_statement.uuid:
                self.schema_statements[st.object] = st.subject

    def update_schema_statements(self):
        to_create = []
        for key in self.schema_keys:
            if not key in self.schema_statements:
                st = Statement(SelfStatement, self.root_statement, key)
                self.sts.save(st)
                self.schema_statements[st.object] = st

    def label_schema_statements(self):
        self.sts.ensure_subject_object(self.root_statement, self.schema_statements['label'], 'root statement')
        for key in self.schema_keys:
            self.sts.ensure_subject_object(self.schema_statements[key], self.schema_statements['label'], key)

    def find_name(self, statement):
        if statement.uuid == self.root_statement.uuid:
            return "ROOT"
        else:
            for k, v in self.schema_statements.items():
                if v.uuid == statement.uuid:
                    return k
            else:
                return None
