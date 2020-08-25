class GeneralError(Exception):
    """Fallback Exception class for when there's no more appropriate solution available."""
    pass

class UserError(Exception):
    """Exception to be raised when the user or client does something wrong."""

class NotFoundError(Exception):
    """Exception to be raised when a requested resource could not be found."""
    pass

class QDValueError(Exception):
    """Something went wrong in serializing, deserializing or using a value."""
    pass

class QDSchemaError(Exception):
    """Something went wrong related to Schemas"""
