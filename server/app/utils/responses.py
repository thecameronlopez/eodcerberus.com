from flask import jsonify

def success(message=None, data=None, status=200):
    payload = {"success": True}
    
    if message:
        payload["message"] = message
        
    if data:
        payload.update(data)
        
    return jsonify(payload), status


def error(message, status=400):
    return jsonify(success=False, message=message), status

