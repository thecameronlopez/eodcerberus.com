from flask import current_app, jsonify

def error_response(error):
    payload = {
        "success": False,
        "error": {
            "type": error.error_type,
            "code": error.error_code,
            "message": error.message
        }
    }
    
    if current_app.debug and getattr(error, "details", None):
        payload["error"]["details"] = error.details
        
    return jsonify(payload), error.status_code