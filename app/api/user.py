"""
endpoints for cards
TODO working on it
"""

from flask import jsonify, url_for, request, g
from . import api
from.errors import forbidden
from .. import db
from ..models import User


@api.route('/users/')
def get_users():
    """get all users by api"""
    pass


@api.route('/user')
def get_current_user():
    """get the information of current user"""
    pass


@api.route('/user/<kname>')
def get_user(kname):
    """search for a user by name"""
    pass


@api.route('/user/<kname>/')
def get_user_cards(kanme):
    """get all cards of a user"""
    pass
