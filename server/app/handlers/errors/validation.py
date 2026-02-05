from .base import AppError

class ValidationError(AppError):
    status_code = 422
    error_type = "validation_error"
    error_code = "VALIDATION_422"