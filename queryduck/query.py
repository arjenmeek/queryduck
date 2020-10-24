from .constants import Component
from .exceptions import UserError


class QueryElement:
    def __repr__(self):
        return f"<{self.__class__.__name__} [...]>"


class QueryEntity(QueryElement):

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
        return f"<{self.__class__.__name__} predicates={self.predicates} target={self.target}>"


class ObjectFor(JoinEntity):
    keyword = "objectfor"
    value_component = Component.OBJECT
    meta = False


class SubjectFor(JoinEntity):
    keyword = "subjectfor"
    value_component = Component.SUBJECT
    meta = False


class Filter(QueryElement):
    pass


class Comparison(Filter):
    num_args = 2

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"<{self.__class__.__name__} lhs={self.lhs} rhs={self.rhs}>"


class UnaryFilter(Filter):
    num_args = 1

    def __init__(self, operand):
        self.operand = operand


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
    num_args = 1

    def __init__(self, by):
        self.by = by


class OrderAscending(Order):
    keyword = "asc"


class OrderDescending(Order):
    keyword = "desc"


class Prefer(QueryElement):
    num_args = 1

    def __init__(self, by):
        self.by = by


class PreferMin(Prefer):
    keyword = "min"


class PreferMax(Prefer):
    keyword = "max"


class Having(QueryElement):
    pass


class HavingComparison(Having):
    num_args = 2

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class HavingUnaryFilter(Filter):
    num_args = 1

    def __init__(self, operand):
        self.operand = operand


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


class HavingIsNull(HavingUnaryFilter):
    keyword = "isnull"


class HavingNotNull(HavingUnaryFilter):
    keyword = "notnull"


class FetchEntity(QueryElement):
    num_args = 1

    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"<{self.__class__.__name__} operand={repr(self.operand)}>"


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


class QDQuery:
    def __init__(self, target):
        self.target = target
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
        print("JOINS:")
        [print(f"    {k}: {repr(v)}") for k, v in self.joins.items()]
        print("FILTERS:")
        [print(f"    {f}") for f in self.filters]
        print("ORDERS:")
        [print(f"    {o}") for o in self.orders]
        print("PREFERS:")
        [print(f"    {p}") for p in self.prefers]
        print("HAVINGS:")
        [print(f"    {h}") for h in self.havings]
        print("FETCHES:")
        [print(f"    {f}") for f in self.fetches]
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

    def filter(self, *comparisons):
        for comparison in comparisons:
            self._prepare_element(comparison.lhs)
            self._prepare_element(comparison.rhs)
            self.filters.append(comparison)
        return self

    def order(self, *orders):
        for order in orders:
            self._prepare_element(order.by)
            self.orders.append(order)
        return self

    def prefer(self, *prefers):
        for prefer in prefers:
            self._prepare_element(prefer.by)
            self.prefers.append(prefer)
        return self

    def having(self, *havings):
        for having in havings:
            self._prepare_element(having.lhs)
            self._prepare_element(having.rhs)
            self.havings.append(having)
        return self

    def fetch(self, *fetches):
        for fetch in fetches:
            self._prepare_element(fetch.operand)
            self.fetches.append(fetch)
        return self

    def limit(self, limit):
        self.limit = limit
