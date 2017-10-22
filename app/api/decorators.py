"""
deals with api permissions
"""

from .errors import forbidden
from functools import wraps
from flask import g



def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def author_required(card):
    """the card here is sipposed to be fetched by `card_or_404`
    it raises a **403** with 'Not the author of the card'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user.kname != card.data.get('author'):
                return forbidden('Not the author of the card.')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
