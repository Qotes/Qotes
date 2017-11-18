"""
endpoints for cards
TODO working on it
"""

from flask import jsonify, url_for, request, g, redirect
from . import api
from.errors import forbidden
from .. import db
from ..models import User, Card


@api.route('/users/', methods=['GET', 'POST'])
def users():
    """get all users by api"""
    pass


@api.route('/user/<kname>', methods=['GET', 'PUT'])
def user(kname):
    """search for a user by name"""
    pass


@api.route('/user/<kname>/')
def user_cards(kanme):
    """get all cards of a user"""
    pass


@api.route('/user')
def get_current_user():
    """get the information of current user"""
    return redirect(url_for('api.user', kname=g.current_user.kname))
