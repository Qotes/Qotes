"""
Views for auth,
simple objects, change the database directly,
the ObjectID is too long,
so chose the email to check,
oauth TODO
"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
# from workdir
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..email import send_email
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    find the user from db.user and check the hash
    TODO refer, check logged
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.user_or_none(email=form.email.data)  # it returns a User
        if user is not None and \
              user.chk_password(user.data.get('pdhs'), form.password.data):
            login_user(user, form.remember_me.data)
            user.ping()                        # loginping notice! update the database
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """log out with a specific route
    and return to the index
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    just save the email and pdhs when registered,
    more information to be appended in profile
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.username.data)
        user.addto_db(form.email.data, form.password.data)    # notice! insert into databse
        token = user.gen_reg_token()
        send_email(form.email.data,
                   'Qotes-Confirm your accout', 'auth/email/confirm',
                   user=user, token=token)
        flash('A confirmation message has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    confirm the register,
    chk_reg_token from app/models.py User
    """
    if User.user_or_none(current_user.kname).data.get('cfm'):
        return redirect(url_for('main.index'))
    if current_user.chk_reg_token(token):
        db.user.update_one(
            {'kname': current_user.kname},
            {'$set': {'cfm': True}}
        )                                           # notice! update the database
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    """
    Checkout the authenticity of the user before evert requests,
    the :param:pinglogin should be at here but it will update the
    database so I moved it to the login.
    """
    if current_user.is_authenticated:
        # pinglogin moved
        if request.endpoint\
                and request.endpoint != 'static' \
                and request.endpoint[:5] != 'auth.' \
                and not User.user_or_none(current_user.kname).data.get('cfm'):
            # notice that to place the query at the last
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    """
    make sure the user has logged in, than
    help the unconfirmed user to confirm or reconfirm
    """
    if current_user.is_anonymous or db.user.find_one({'kname': current_user.kname}).get('cfm'):
                       # it could also be User.user_or_none(current_user.kname).data.get('cfm')
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """resend the confirm email,
    I have to use the email, so there's a query.
    """
    token = current_user.gen_reg_token()
    send_email(current_user.email,                     # query the database
               'Qotes-Confirm your accout', 'auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
