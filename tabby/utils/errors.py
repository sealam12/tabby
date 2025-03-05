class ModelNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MismatchedTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class NotNullConstraintError(Exception):
    def __init__(self, message):
        super().__init__(message)