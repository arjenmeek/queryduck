from .constants import Component
from .serialization import serialize
from .exceptions import UserError


class QueryElement:
    def __repr__(self):
        return f"<{self.__class__.__name__} [...]>"

    def get_operands(self):
        return []


class QueryEntity(QueryElement):
    maintype = "join"

    def __str__(self):
        return f"alias:{self.key}"

    def __eq__(self, other):
        return Equals(self, other)

    def __ne__(self, other):
        return NotEquals(self, other)

    def __lt__(self, other):
        return Less(self, other)

    def __le__(self, other):
        return LessEqual(self, other)

    def __gt__(self, other):
        return Greater(self, other)

    def __ge__(self, other):
        return GreaterEqual(self, other)

    def object_for(self, *predicates):
        return ObjectFor(predicates, self)

    def subject_for(self, *predicates):
        return SubjectFor(predicates, self)

    def fetch(self):
        return FetchEntity(self)

    def order_asc(self, vtype):
        return OrderAscending(self, vtype)


class Main(QueryEntity):
    keyword = "main"
    value_component = Component.SELF

    def __init__(self):
        self.key = "main"
        self.target = None

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class JoinEntity(QueryEntity):
    num_args = 3

    def __init__(self, predicates, target=None, key=None):
        self.predicates = predicates
        self.target = target
        self.key = key

    def __repr__(self):
        return f"<{self.__class__.__name__} predicates={self.predicates} target={self.target} key={self.key}>"

    @classmethod
    def deserialize(cls, string, callback):
        target_string, key, *predicate_strs = string.split(",")
        target = callback(target_string)
        predicates = [callback(ps) for ps in predicate_strs]
        return cls(predicates, target, key)

    def serialize(self, callback):
        parts = [callback(self.target), self.key]
        parts += [callback(p) for p in self.predicates]
        return ",".join(parts)


class ObjectFor(JoinEntity):
    keyword = "objectfor"
    value_component = Component.OBJECT
    meta = False


class SubjectFor(JoinEntity):
    keyword = "subjectfor"
    value_component = Component.SUBJECT
    meta = False


class Filter(QueryElement):
    maintype = "filter"


class Comparison(Filter):
    num_args = 2

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"<{self.__class__.__name__} lhs={self.lhs} rhs={self.rhs}>"

    @classmethod
    def deserialize(cls, string, callback):
        lhs_string, rhs_string = string.split(",")
        lhs, rhs = callback(lhs_string), callback(rhs_string)
        return cls(lhs, rhs)

    def serialize(self, callback):
        return f"{callback(self.lhs)},{callback(self.rhs)}"

    def get_operands(self):
        return [self.lhs, self.rhs]


class UnaryFilter(Filter):
    num_args = 1

    def __init__(self, operand):
        self.operand = operand

    def get_operands(self):
        return [self.operand]


class Equals(Comparison):
    keyword = "eq"


class NotEquals(Comparison):
    keyword = "ne"


class Less(Comparison):
    keyword = "lt"


class LessEqual(Comparison):
    keyword = "le"


class Greater(Comparison):
    keyword = "gt"


class GreaterEqual(Comparison):
    keyword = "ge"


class IsNull(UnaryFilter):
    keyword = "isnull"


class NotNull(UnaryFilter):
    keyword = "notnull"


class Order(QueryElement):
    maintype = "order"
    num_args = 2

    def __init__(self, by, vtype):
        self.by = by
        self.vtype = vtype

    def __repr__(self):
        return f"<{self.__class__.__name__} by={self.by} vtype={self.vtype}>"

    @classmethod
    def deserialize(cls, string, callback):
        target_string, vtype = string.split(",")
        target = callback(target_string)
        return cls(target, vtype)

    def serialize(self, callback):
        return f"{callback(self.by)},{self.vtype}"

    def get_operands(self):
        return [self.by]


class OrderAscending(Order):
    keyword = "asc"


class OrderDescending(Order):
    keyword = "desc"


class Prefer(QueryElement):
    maintype = "prefer"
    num_args = 1

    def __init__(self, by):
        self.by = by

    def get_operands(self):
        return [self.by]


class PreferMin(Prefer):
    keyword = "min"


class PreferMax(Prefer):
    keyword = "max"


class Having(QueryElement):
    maintype = "having"


class HavingComparison(Having):
    num_args = 2

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_operands(self):
        return [self.lhs, self.rhs]


class HavingUnary(Having):
    num_args = 1

    def __init__(self, operand):
        self.operand = operand

    def get_operands(self):
        return [self.operand]


class HavingEquals(HavingComparison):
    keyword = "eq"


class HavingNotEquals(HavingComparison):
    keyword = "ne"


class HavingLess(HavingComparison):
    keyword = "lt"


class HavingLessEqual(HavingComparison):
    keyword = "le"


class HavingGreater(HavingComparison):
    keyword = "gt"


class HavingGreaterEqual(HavingComparison):
    keyword = "ge"


class HavingIsNull(HavingUnary):
    keyword = "isnull"


class HavingNotNull(HavingUnary):
    keyword = "notnull"


class FetchEntity(QueryElement):
    maintype = "fetch"
    keyword = "entity"
    num_args = 1

    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"<{self.__class__.__name__} operand={repr(self.operand)}>"

    @classmethod
    def deserialize(cls, string, callback):
        operand = callback(string)
        return cls(operand)

    def serialize(self, callback):
        callback(self.operand)

    def get_operands(self):
        return [self.operand]


element_classes = {
    ("join", "objectfor"): ObjectFor,
    ("join", "subjectfor"): SubjectFor,
    ("filter", "eq"): Equals,
    ("filter", "ne"): NotEquals,
    ("filter", "lt"): Less,
    ("filter", "le"): LessEqual,
    ("filter", "gt"): Greater,
    ("filter", "ge"): GreaterEqual,
    ("filter", "isnull"): IsNull,
    ("filter", "notnull"): NotNull,
    ("order", "asc"): OrderAscending,
    ("order", "desc"): OrderDescending,
    ("prefer", "min"): PreferMin,
    ("prefer", "max"): PreferMax,
    ("having", "eq"): HavingEquals,
    ("having", "ne"): HavingNotEquals,
    ("having", "lt"): HavingLess,
    ("having", "le"): HavingLessEqual,
    ("having", "gt"): HavingGreater,
    ("having", "ge"): HavingGreaterEqual,
    ("having", "isnull"): HavingIsNull,
    ("having", "notnull"): HavingNotNull,
    ("fetch", "entity"): FetchEntity,
}


def query_to_request_params(query):
    def callback(value):
        if isinstance(value, QueryEntity):
            return f"alias:{value.key}"
        else:
            return serialize(value)

    params = []
    for e in query.elements:
        key = f"{e.maintype}.{e.keyword}"
        val = e.serialize(callback)
        params.append((key, val))
    return params


class QDQuery:
    def __init__(self, target):
        self.target = target
        self.elements = []
        self.joins = {}
        self.filters = []
        self.orders = []
        self.prefers = []
        self.havings = []
        self.fetches = []
        self.limit = 1000
        self.seen_values = set()

    def show(self):
        print("------ START QUERY SUMMARY ------")
        print("ELEMENTS:")
        [print(f"    {repr(e)}") for e in self.elements]
        print("JOINS:")
        [print(f"    {k}: {repr(v)}") for k, v in self.joins.items()]
        print("LIMIT:", self.limit)
        print("------ END QUERY SUMMARY ------")

    def _get_join_key(self, prefix="join"):
        for i in range(1, 1000):
            try_key = f"{prefix}{i}"
            if not try_key in self.joins:
                return try_key
        raise UserError("Too many joins")

    def join(self, entity):
        if isinstance(entity, JoinEntity):
            [self.seen_values.add(p) for p in entity.predicates]
        current = entity
        stack = []
        while current:
            if not current.key:
                current.key = self._get_join_key()
            if not current.key in self.joins:
                stack.append(current)
            current = current.target
        for e in reversed(stack):
            self.joins[e.key] = e
        return self

    def _prepare_element(self, element):
        if isinstance(element, QueryEntity):
            self.join(element)
        else:
            self.seen_values.add(element)

    def add(self, *elements):
        for element in elements:
            if isinstance(element, QueryEntity):
                self.join(element)
            [self._prepare_element(o) for o in element.get_operands()]
            self.elements.append(element)
        return self

    def get_elements(self, cls):
        elements = [e for e in self.elements if isinstance(e, cls)]
        return elements

    def limit(self, limit):
        self.limit = limit
