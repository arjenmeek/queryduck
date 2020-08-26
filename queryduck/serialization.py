from .types import serialize, Inverted, Statement

def parse_identifier(repo, bindings, identifier):
    if ':' in identifier:
        v = repo.unique_deserialize(identifier)
    elif identifier in bindings:
        v = bindings[identifier]
    else:
        v = identifier
    return v

def make_identifier(result, bindings, value):
    b = bindings
    if b.reverse_exists(value):
        return b.reverse(value)
    elif type(value) == Inverted and b.reverse_exists(value.value):
        return "~{}".format(b.reverse(value.value))
    elif type(value) == Statement:
        types = [s.triple[2] for s in
            result.find(s=value, p=b.type)]
        type_elements = [b.reverse(t) for t in types if t != b.Resource]
        type_elements = list(filter(None, type_elements))
        labels = [s.triple[2] for s in
            result.find(s=value, p=b.label)]
        if len(type_elements) and len(labels):
            return '/'.join([''] + type_elements + labels[0:1])
    return value if type(value) in (str, int) else serialize(value)
