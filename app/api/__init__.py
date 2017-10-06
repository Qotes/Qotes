"""
This is supposed to be the only version of API
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import user, card, errors, authuentication
