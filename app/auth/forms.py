"""
login forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .. import db


class LoginForm(FlaskForm):
    """Oauth should be add to somewhere different,
    it may be a modal or something different,
    as this form is also used in the navbar.
    """
    email = StringField('Email', validators=[Required(), Length(1, 28), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """only inserts email, kname and pdhs to db,
    more information can be appended later
    """
    email = StringField('Email', validators=[Required(), Length(1, 28), Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 28),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """auto check wether email in use
        """
        if db.user.find_one({'email':field.data}):               # notice query
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """auto check wether username in use
        """
        if db.user.find_one({'kname':field.data}):               # notice query
            raise ValidationError('Username already in use.')
