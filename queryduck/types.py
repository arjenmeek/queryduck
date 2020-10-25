import abc
import base64
import datetime
import uuid

from collections import defaultdict
from decimal import Decimal

from .exceptions import QDValueError


class CompoundValue(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass


class Statement(CompoundValue):
    target_name = "statement"

    def __init__(self, handle=None, id_=None, triple=None):
        self.handle = uuid.UUID(handle) if type(handle) == str else handle
        self.id = id_
        self.triple = triple
        self.saved = False

    def __repr__(self):
        parts = [
            "{}={}".format(k, getattr(self, k))
            for k in ("handle", "id")
            if getattr(self, k) is not None
        ]
        if self.triple:
            parts.append("complete")
        return "<Statement {}>".format(" ".join(parts))


class Blob(CompoundValue):
    target_name = "blob"

    def __init__(self, serialized=None, handle=None, id_=None):
        self.id = id_
        self.handle = base64.urlsafe_b64decode(serialized) if handle is None else handle

    def encoded_handle(self):
        r = (
            None
            if self.handle is None
            else base64.urlsafe_b64encode(self.handle).decode("utf-8")
        )
        return r

    def serialize(self):
        return self.encoded_handle()

    def __repr__(self):
        return "<Blob id={} handle={}>".format(
            self.id, None if self.handle is None else self.encoded_handle()
        )


class File:
    def __init__(self, serialized=None, volume=None, path=None):
        if serialized:
            ser_opts, self.volume, ser_path = serialized.split(":", 2)
            opts = ser_opts.split(",")
            if "b64" in opts:
                self.path = base64.urlsafe_b64decode(ser_path)
            else:
                self.path = ser_path.encode()
        else:
            self.volume = volume
            self.path = path

    def __repr__(self):
        return '<File volume="{}" path="{}">'.format(self.volume, self.path.decode())

    def serialize(self):
        try:
            return ":{}:{}".format(self.volume, self.path.decode())
        except UnicodeDecodeError:
            return "b64:{}:{}".format(
                self.volume, base64.urlsafe_b64encode(self.path).decode()
            )


class Placeholder:
    def __init__(self, id_):
        self.id = id_

    def __repr__(self):
        return "<Placeholder {}>".format(self.id)


value_types = {
    "int": {
        "type": int,
        "factory": int,
        "column_name": "object_integer",
        "serializer": str,
    },
    "bool": {
        "type": bool,
        "factory": bool,
        "column_name": "object_boolean",
        "serializer": str,
    },
    "bytes": {
        "type": bytes,
        "factory": lambda b: base64.urlsafe_b64decode(b),
        "column_name": "object_bytes",
        "serializer": lambda b: base64.urlsafe_b64encode(b).decode("utf-8"),
    },
    "dec": {
        "type": Decimal,
        "factory": Decimal,
        "column_name": "object_decimal",
        "serializer": str,
    },
    "str": {
        "type": str,
        "factory": str,
        "column_name": "object_string",
        "serializer": str,
    },
    "datetime": {
        "type": datetime.datetime,
        "factory": lambda dt: datetime.datetime.fromisoformat(dt),
        "column_name": "object_datetime",
        "serializer": lambda dt: dt.isoformat(),
    },
    "s": {
        "type": Statement,
        "factory": Statement,
        "column_name": "object_statement_id",
        "serializer": lambda s: s.handle,
    },
    "blob": {
        "type": Blob,
        "factory": Blob,
        "column_name": "object_blob_id",
        "serializer": lambda b: b.serialize(),
    },
    "none": {
        "type": type(None),
        "factory": lambda x: None,
        "column_name": "id",  # for "IS NULL" comparison
        "serializer": str,
    },
    "file": {
        "type": File,
        "factory": File,
        "serializer": lambda f: f.serialize(),
    },
}

value_types_by_native = {
    int: "int",
    bool: "bool",
    bytes: "bytes",
    Decimal: "dec",
    str: "str",
    datetime.datetime: "datetime",
    Statement: "s",
    Blob: "blob",
    type(None): "none",
    File: "file",
}

value_comparison_methods = {
    "eq": "__eq__",
    "ne": "__ne__",
    "gt": "__gt__",
    "ge": "__ge__",
    "lt": "__lt__",
    "le": "__le__",
    "contains": "contains",
    "startswith": "startswith",
    "endswith": "endswith",
    "in": "in_",
}

list_comparison_methods = {
    "in": "in_",
}
