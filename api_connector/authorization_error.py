

class AuthorizationError(Exception):
    """Custom exception for handling authorization errors."""

    def __init__(self, 
                 message: str, 
                 error_code: int = None, 
                 details: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self):
        error_msg = f"AuthorizationError: {self.message}"
        if self.error_code is not None:
            error_msg += f" (Error Code: {self.error_code})"
        if self.details:
            error_msg += f" Details: {self.details}"
        return error_msg