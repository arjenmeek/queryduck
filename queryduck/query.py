from .constants import Component


class QueryElement:
    pass


class QueryEntity(QueryElement):
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

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

    def object_for(self, predicate):
        return ObjectFor(predicate, self)

    def subject_for(self, predicate):
        return SubjectFor(predicate, self)


class Main(QueryEntity):
    keyword = "main"
    value_component = Component.SELF

    def __init__(self):
        self.key = "main"
        self.target = None


class JoinEntity(QueryEntity):
    num_args = 3

    def __init__(self, predicate, target=None, key=None):
        self.predicate = predicate
        self.target = target
        self.key = key


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
}


class QDQuery:
    def __init__(self, target):
        self.target = target
        self.joins = {}
        self.filters = []
        self.orders = []
        self.prefers = []
        self.havings = []
        self.limit = 1000
        self.seen_values = set()

    def join(self, entity):
        if isinstance(entity, JoinEntity):
            self.seen_values.add(entity.predicate)
        current = entity
        stack = []
        while current:
            if not current.key:
                current.key = "dummykey"
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

    def limit(self, limit):
        self.limit = limit
