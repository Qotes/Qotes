"""
auth blueprint
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

# to avoid import loops
from . import views
