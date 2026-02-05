from flask import jsonify
from marshmallow import ValidationError
from .base import AppError
from .response import error_response


def register_error_handlers(app):
    
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return error_response(err)
    
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error_response(
            AppError(
                message="Validation error",
                code="SCHEMA_422",
                details=err.messages
            )
        )
        
        
    @app.errorhandler(404)
    def not_found(_):
        return error_response(
            AppError("Resource not found", code="HTTP_404")
        )
        
        
    @app.errorhandler(405)
    def method_not_allowed(_):
        return error_response(
            AppError("Method not allowed", code="HTTP_405")
        )
        
        
    @app.errorhandler(Exception)
    def unhandled_exception(err):
        if app.debug:
            raise err
        
        return jsonify({
            "success": False,
            "error": {
                "type": "internal_error",
                "code": "SERVER_500",
                "message": "Internal server error"
            }
        }), 500