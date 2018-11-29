from .utility import serialize_value

class StatementFilter():

    def __init__(self, lhs, operand, rhs=None):
        self.lhs = lhs
        self.operand = operand
        self.rhs = rhs

    def serialize(self):
        serialized_parts = [serialize_value(self.lhs)]
        serialized_parts.append(self.operand)
        if self.rhs is not None:
            serialized_parts.append(serialize_value(self.rhs))
        serialized = ','.join(serialized_parts)
        return serialized
