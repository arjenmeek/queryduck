import uuid

from crunchylib.exceptions import GeneralError
from crunchylib.utility import StatementReference, serialize_value


class Statement(object):

    def __init__(self, uuid_, subject, predicate, object_, statement_repository=None):
        self.uuid = uuid_
        self._subject = subject
        self._predicate = predicate
        self._object = object_
        self._statement_repository = statement_repository

    @property
    def subject(self):
        if isinstance(self._subject, StatementReference):
            self._subject = self._subject.resolve(self, self._statement_repository)
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def predicate(self):
        if isinstance(self._predicate, StatementReference):
            self._predicate = self._predicate.resolve(self, self._statement_repository)
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        self._predicate = value

    @property
    def object(self):
        if isinstance(self._object, StatementReference):
            self._object = self._object.resolve(self, self._statement_repository)
        return self._object

    @object.setter
    def object(self, value):
        self._object = value

    def show(self):
        s_values = [serialize_value(v) for v in [self.uuid, self._subject, self._predicate, self._object]]
        print(*s_values)
