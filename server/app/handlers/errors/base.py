class AppError(Exception):
    status_code = 400
    error_type = "application_error"
    error_code = "APP_000"
    
    def __init__(self, message=None, *, code=None, details=None):
        super().__init__(message)
        self.message = message or "An error occurred"
        self.code = code or self.error_code
        self.details = details
