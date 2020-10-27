from .exceptions import QDValueError
from .types import Statement, value_types, value_types_by_native


def get_native_vtype(native_value):
    vtype = value_types_by_native[type(native_value)]
    return vtype


def process_serialized_value(serialized_value):
    vtype, ser_v = serialized_value.split(":", 1)
    if not vtype in value_types:
        raise QDValueError("Invalid value type: {}".format(vtype))
    v = value_types[vtype]["factory"](ser_v)
    return v, vtype


def serialize(native_value):
    prefix = ""

    vtype = get_native_vtype(native_value)
    if vtype == "filter":
        return native_value.op

    serialized = "{}{}:{}".format(
        prefix, vtype, value_types[vtype]["serializer"](native_value)
    )
    return serialized


def deserialize(serialized_value):
    cls = None

    v, vtype = process_serialized_value(serialized_value)
    if cls:
        v = cls(v)
    return v


def parse_identifier(repo, bindings, identifier):
    cls = None

    if ":" in identifier:
        v = repo.unique_deserialize(identifier)
    elif identifier in bindings:
        v = bindings[identifier]
    elif identifier.startswith("/"):
        dummy, *resources, label = identifier.split("/")
        result, coll = repo.query({MatchObject(bindings.label): label})
        v = label
    else:
        v = identifier

    if cls:
        v = cls(v)

    return v


def make_identifier(result, bindings, value):
    b = bindings
    prefix = ""

    if b.reverse_exists(value):
        return prefix + b.reverse(value)
    elif type(value) == Statement:
        types = [s.triple[2] for s in result.find(s=value, p=b.type)]
        type_elements = [b.reverse(t) for t in types if t != b.Resource]
        type_elements = list(filter(None, type_elements))
        labels = [s.triple[2] for s in result.find(s=value, p=b.label)]
        if len(type_elements) and len(labels):
            return prefix + "/".join([""] + type_elements + labels[0:1])
    return prefix + serialize(value)
