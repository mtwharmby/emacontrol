class EmaException(Exception):
    """
    A base class for all custom exceptions that might be thrown from the EMA
    classes
    """
    def __init__(self, msg=None, *args):
        if msg is None:
            msg = "An error occurred executing EMA motion"
        super().__init__(msg, *args)


class EmaCommunicationException(EmaException):
    """
    Exception to be thrown when a communication problems occur.
    """
    def __init__(self, msg=None, *args):
        super().__init__(self, msg, *args)


