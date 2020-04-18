def transform_doc(doc, transform):
    """Transform any scalar key or value in nested document structure.

    This function assumes doc consists entirely of list, dict and scalar
    values, more complex types are not accounted for. This should be fine for
    any regular JSON-style document, but more complex value types may lead to
    unexpected results.
    """
    in_stack = [('doc', doc)]
    out_stack = []
    new = cur = {}
    while in_stack:
        v = in_stack.pop()
        while v is None and in_stack:
            v = in_stack.pop()
            cur = out_stack.pop()

        val = v[1] if type(v) == tuple else v
        t = type(val)
        if t in (dict, list):
            in_stack += [None] + ( val if t == list
                else list(val.items()) )[::-1]
            val = t()
        elif val is not None:
            val = transform(val)

        if type(v) == tuple:
            cur[transform(v[0])] = val
        elif v is not None:
            cur.append(val)
        if t in (dict, list):
            out_stack.append(cur)
            cur = val
    return new['doc']
