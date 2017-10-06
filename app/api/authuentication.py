"""
authenticaton for the request
"""

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from . import api
from .errors import unauthorized

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    """
    the user is supposed to verify by email or token,
    and the g.current_user will be a User instance with data
    """
    if email_or_token == '':             # Anonymous
        g.current_user = AnonymousUser()
        return True
    if password == '':                   # token
        g.current_user = User.chk_api_token(email_or_token)
        g.token_used = True        # So don't use this if token not used
        return g.current_user.data != {}
    user = User.user_or_none(email=email_or_token)  # it's a User
    if not user.data:
        return False
    g.current_user = user
    return user.chk_password(user.data.get('pdhs'), password)


@auth.error_handler
def auth_error():
    """docstr"""
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    """
    There is no constrain for visiting the site through apis as long
    as logged.
    """
    pass


@api.route('/token')
def gen_token():
    """
    Generates a token if token is not in use.
    """
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.gen_api_token(),
        'expiration': 604800
    })
