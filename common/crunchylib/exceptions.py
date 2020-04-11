class GeneralError(Exception):
    """Fallback Exception class for when there's no more appropriate solution available."""
    pass

class NotFoundError(Exception):
    """Exception to be raised when a requested resource could not be found."""
    pass

class CVValueError(Exception):
    """Something went wrong in serializing, deserializing or using a value."""
    pass
