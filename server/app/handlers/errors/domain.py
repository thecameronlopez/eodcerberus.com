from .base import AppError

class NotFoundError(AppError):
    status_code = 404
    error_type = "not_found"
    error_code = "RESOURCE_404"
    
    
class PermissionDenied(AppError):
    status_code = 403
    error_type = "permission_denied"
    error_code = "AUTH_403"
    
    
class ConflictError(AppError):
    status_code = 409
    error_type = "conflict"
    error_code = "RESOURCE_409"