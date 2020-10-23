import enum

DEFAULT_SCHEMA_FILES = [
    "main_schema.json",
    "transaction_schema.json",
    "storage_schema.json",
]


class Component(enum.Enum):
    SELF = enum.auto
    SUBJECT = enum.auto
    PREDICATE = enum.auto
    OBJECT = enum.auto
