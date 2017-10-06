"""
return a default response for several exceptions,
by Miguel Grinberg
"""

from flask import jsonify
from . import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def notfound(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response



class ValidationError(ValueError):
    pass


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.errorhandler(404)
def not_found(e):
    return jsonify({'404': 'NOT FOUND'}), 404
