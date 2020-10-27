from .serialization import serialize, make_identifier


def transform_doc(doc, transform):
    """Transform any scalar key or value in nested document structure.

    This function assumes doc consists entirely of list, dict and scalar
    values, more complex types are not accounted for. This should be fine for
    any regular JSON-style document, but more complex value types may lead to
    unexpected results.
    """
    in_stack = [doc]
    out_stack = []
    new = None
    while in_stack:
        v = in_stack.pop()
        while v is None and in_stack:
            v = in_stack.pop()
            cur = out_stack.pop()

        val = v[1] if type(v) == tuple else v
        t = type(val)
        if t in (dict, list):
            in_stack += [None] + (val if t == list else list(val.items()))[::-1]
            val = t()
        elif val is not None:
            val = transform(val)

        if new is None:
            new = cur = val
        elif type(v) == tuple:
            cur[transform(v[0])] = val
        elif v is not None:
            cur.append(val)
        if t in (dict, list):
            out_stack.append(cur)
            cur = val
    return new


class DocProcessor:
    def __init__(self, coll, bindings):
        self.coll = coll
        self.bindings = bindings

    def value_to_doc(self, value):
        b = self.bindings
        main_parent = {"main": {}}
        stack = [(value, main_parent, "main", 0)]
        i = 0
        while stack:
            v, parent, key, depth = stack.pop()
            object_statements = [s for s in self.coll.find(s=v) if s != s.triple[2]]
            if (
                not (b.reverse_exists(v) and depth >= 1)
                and type(v).__name__ == "Statement"
                and len(object_statements)
            ):
                sub = {}
                if b.reverse_exists(v):
                    sub["="] = "{} ({})".format(b.reverse(v), serialize(v))
                else:
                    sub["="] = serialize(v)

                labels = self.coll.objects_for(v, b.label)
                for l in labels:
                    if type(l) == str:
                        label = l
                        break
                else:
                    label = None
                    break

                types = self.coll.objects_for(v, b.type)
                if b.Resource in types:
                    otypes = [t for t in types if t != b.Resource]
                    btypes = [b.reverse(t) for t in otypes if b.reverse_exists(t)]
                    if label and len(btypes):
                        sub["/"] = "/".join([""] + btypes + [label])

                for s in object_statements:
                    if s.triple[2] == s:
                        continue
                    subkey = "{}".format(b.reverse(s.triple[1]))
                    stack.append((s.triple[2], sub, subkey, depth + 1))

                if key in parent and depth >= 1:
                    if type(parent[key]) != list:
                        parent[key] = [parent[key]]
                    parent[key].append(sub)
                else:
                    parent[key] = sub
            else:
                val = b.reverse(v) if b.reverse_exists(v) else serialize(v)
                if key in parent:
                    if type(parent[key]) != list:
                        parent[key] = [parent[key]]
                    parent[key].append(val)
                else:
                    parent[key] = val
        return main_parent["main"]


def safe_bytes(input_bytes):
    """Replace surrogates in UTF-8 bytes"""
    return input_bytes.decode("utf-8", "replace").encode("utf-8")


def safe_string(input_string):
    """Replace surrogates in UTF-8 string"""
    return input_string.encode("utf-8", "replace").decode("utf-8")


class CombinedIterator:
    def __init__(self, left, right, left_key, right_key):
        self.left = left
        self.right = right
        self.left_key = left_key
        self.right_key = right_key
        self._advance_left()
        self._advance_right()

    def __iter__(self):
        return self

    def _advance_left(self):
        if self.left is not None:
            try:
                self.cur_left = next(self.left)
            except StopIteration:
                self.left = None
                self.cur_left = None

    def _advance_right(self):
        if self.right is not None:
            try:
                self.cur_right = next(self.right)
            except StopIteration:
                self.right = None
                self.cur_right = None

    def __next__(self):
        if self.left is None and self.right is None:
            raise StopIteration
        elif self.right is None or (
            self.left is not None
            and self.left_key(self.cur_left) < self.right_key(self.cur_right)
        ):
            retval = (self.cur_left, None)
            self._advance_left()
        elif self.left is None or self.left_key(self.cur_left) > self.right_key(
            self.cur_right
        ):
            retval = (None, self.cur_right)
            self._advance_right()
        else:
            retval = (self.cur_left, self.cur_right)
            self._advance_left()
            self._advance_right()

        return retval
