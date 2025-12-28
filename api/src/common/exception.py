class AppBaseException(Exception):
    """Base exception class for the application"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(AppBaseException):
    """Data validation exception"""
    def __init__(self, message: str):
        super().__init__(message, 400)