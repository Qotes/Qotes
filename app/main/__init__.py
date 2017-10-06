"""
basic main blueprint
"""

from flask import Blueprint

main = Blueprint('main', __name__)

# to avoid import loops
from . import views, errors
