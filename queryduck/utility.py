from .types import serialize, Inverted
from .serialization import make_identifier

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
            in_stack += [None] + ( val if t == list
                else list(val.items()) )[::-1]
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

def value_to_doc(result, bindings, value):
    r = value
    statements = result.find(s=r)
    doc = {
        '_s': serialize(r),
        '_r': make_identifier(result, bindings, r),
    }
    for s in statements:
        if not s.triple[1] in doc:
            doc[s.triple[1]] = []
        if s.triple[0] != s:
            meta = result.find(s=s)
        else:
            meta = []
        if meta:
            val = {'+': s.triple[2]}
            for m in meta:
                key = make_identifier(result, bindings, m.triple[1])
                if not key in val:
                    val[key] = []
                val[key].append(make_identifier(result, bindings, m.triple[2]))
            val = {k: v if k == '+' or len(v) != 1 else v[0] for k, v in val.items()}
        else:
            val = s.triple[2]
        doc[s.triple[1]].append(val)
    inverse_statements = result.find(o=r)
    for s in inverse_statements:
        inv = Inverted(s.triple[1])
        if not inv in doc:
            doc[inv] = []
        doc[inv].append(s.triple[0])
    doc = {k: v[0] if type(v) == list and len(v) == 1 else v
        for k, v in doc.items()}
    def my_make_identifier(v):
        return make_identifier(result, bindings, v)
    doc = transform_doc(doc, my_make_identifier)
    return doc

def safe_bytes(input_bytes):
    """Replace surrogates in UTF-8 bytes"""
    return input_bytes.decode('utf-8', 'replace').encode('utf-8')

def safe_string(input_string):
    """Replace surrogates in UTF-8 string"""
    return input_string.encode('utf-8', 'replace').decode('utf-8')


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
                print("thisisnext")
            except StopIteration:
                self.left = None
                self.cur_left = None
                print("thisisexception")
        print("NEXT", str(self.cur_left).encode(errors='ignore'), type(self.cur_left))

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
        elif (self.right is None or
                self.left_key(self.cur_left) < self.right_key(self.cur_right)):
            retval = (self.cur_left, None)
            self._advance_left()
        elif (self.left is None or
                self.left_key(self.cur_left) > self.right_key(self.cur_right)):
            retval = (None, self.cur_right)
            self._advance_right()
        else:
            retval = (self.cur_left, self.cur_right)
            self._advance_left()
            self._advance_right()

        return retval
