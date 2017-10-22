"""
endpoints for basic logic, mainly consistsof the index, the cardpage
and the userpage. Some specific functions dealing with the cards
are also included.
"""

from pymongo import DESCENDING
from flask import render_template, flash, abort, redirect, url_for, request
from flask_login import login_user, current_user, login_required
from bson.objectid import ObjectId
from . import main
from .forms import WriteForm, EditAboutmeForm, QuickCardForm
from .. import db
from ..models import User, Card, Pagination, Permission
from ..auth.forms import LoginForm


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    two forms and an area of posts
    search form TODO
    """
    if current_user.is_authenticated:
        quickcard_form = QuickCardForm()
        cursor = db.card.find({'dad': current_user.kname})
        current_page = request.args.get('page') or 1
        pagination = Pagination(cursor, current_page)
        cards = pagination.page                                   # it is a cursor
        if quickcard_form.validate_on_submit():
            card = Card(current_user.kname, quickcard_form.content.data)
            card.addto_db()                      # notice! insert into the db
            return redirect(url_for('main.index'))
        return render_template('indexl.html',
                               quickcard_form=quickcard_form,
                               pagination=pagination,
                               cards=cards)      # the cards here is a cursor
    else:
        nav_login_form = LoginForm()
        # login in dropdown
        if nav_login_form.validate_on_submit():
            user = User.user_or_none(email=nav_login_form.email.data)  # it returns a User
            if user is not None and \
                  user.chk_password(user.data.get('pdhs'), nav_login_form.password.data):
                login_user(user, nav_login_form.remember_me.data)
                user.ping()                        # loginping notice! update the database
            else:
                flash('Invalid username or password.')
            return redirect(url_for('main.index'))        # POST-REDIRECT-GET
        return render_template('index.html',
                               nav_login_form=nav_login_form)


@main.route('/user/<username>', methods=['GET', 'POST'])
def userpage(username):
    """user's personal page,
    there's much information to use,
    so use the dict to work with the template
    """
    # block the view of other users
    if username != 'sy':
        if not current_user.can(Permission.READ_ALL):
        # if current_user.kname != username and current_user.kname != 'sy': this also works
            flash('I have to let you stay here for some reason.')
            return redirect(url_for('main.userpage', username='sy'))
    # normal
    aboutme_form = EditAboutmeForm()
    user = db.user.find_one({'kname': username})                # it's a dict
    if user is None:
        abort(404)
    # posts
    cursor = Card.get_sons(username, current_user.kname, username)   # cursor
    # pagination
    current_page = request.args.get('page') or 1
    pagination = Pagination(cursor, current_page)
    cards = pagination.page                                   # it is a cursor
    # TODO CHECK WHETHER CURSOR DEAD IF QUERIED AGAIN
    latestcards = db.card.find({'author': username, 'prvt': False}).sort('since', DESCENDING).limit(5)
    if current_user.kname == username and aboutme_form.validate_on_submit():
        db.user.update_one(
            {'kname': username},
            {'$set': {'aboutme': aboutme_form.aboutme.data}}
        )                                       # notice！ update the database
        flash('About me edited.')
        return redirect(url_for('main.userpage', username=username))  # POST-REDIRECT-GET
    return render_template('user.html', user=user,       # the user is a dict
                           aboutme_form=aboutme_form,
                           pagination=pagination,
                           latestcards=latestcards,     # the latestcards is a cursor
                           cards=cards)           # the cards here is a list of dicts


@main.route('/write', methods=['POST', 'GET'])
@login_required
def write():
    """
    if linked from userpage or index, it produces a wildcard, or else the card will
    be a subcard
    """
    form = WriteForm()
    if form.validate_on_submit():
        card = Card(current_user.kname, form.content.data)
        fatherid = request.args.get('from')
        # check the identity
        if fatherid:
            if current_user.kname != Card.card_or_404(fatherid).data.get('author'):
                flash('Permission denied')
                return redirect(url_for('main.write'))
        # add it to db
        card.addto_db(fatherid=fatherid)        # notice! insert into db
        flash('Card posted')
        return redirect(url_for('main.write'))
    return render_template('card/write.html', form=form)


@main.route('/card/<cardid>', methods=['POST', 'GET'])
def cardpage(cardid):
    """
    show the sons of a card or user
    """
    card = Card.card_or_404(cardid)                           # it's a Card
    # for pagination
    cursor = Card.get_sons(cardid, current_user.kname, card.data.get('author'))    # cursor
    current_page = request.args.get('page') or 1
    pagination = Pagination(cursor, current_page)
    cards = pagination.page                                   # it is a cursor
    # for sidebar
    fatherid = card.data.get('dad')
    father = User.user_or_none(fatherid)               # not confirmed
    fathername = father.data.get('kname') or Card.card_or_404(fatherid).data.get('title')
    if father.data.get('kname'):
        fatherlink = url_for('main.userpage', username=fathername)
    else:
        fatherlink = url_for('main.cardpage', cardid=fatherid)
    siblings = Card.get_sons(card.data.get('dad'), current_user.kname, card.data.get('author'))
    sidebar = [fathername, siblings.limit(20), fatherlink]
    # blocked in html --------------------------------------------------------------------
    # I blocked this method right now as I haven't found a nice way to transfer html to md
    # I decided to make this available when I finish the editor by my own
    # quickcard_form = QuickCardForm()
    # if quickcard_form.validate_on_submit():
    #     Card.edit(cardid, quickcard_form.content.data, is_html=True)
    #     flash('Card edited.')
    #     return redirect(url_for('main.cardpage', cardid=cardid))  # POST-REDIRECT-GET
    # blocked in html --------------------------------------------------------------------
    return render_template('card/card.html',
                           # quickcard_form=quickcard_form,
                           card=card,
                           pagination=pagination,
                           sidebar=sidebar,
                           cards=cards)


@main.route('/card/addson/<father>/<son>')
@login_required
def addson(father, son):
    """
    Add one card to another by draw and drop,
    only in userpage.There should be an if but as
    I'm gonna restruct it I will leave it here.

    This shit is too ugly!!! and insecure!!!!!
    TODO change it to ajax after API completed.
    """
    if father and son and father != son:            # notice! update database
        db.card.update_one({'_id': ObjectId(son)}, {'$set': {'dad': father}})
        flash('Card moved.')
    return redirect(url_for('main.userpage', username=current_user.kname))


@main.route('/card/edit/<cardid>', methods=['POST', 'GET'])
@login_required
def edit(cardid):
    """
    I used a hidden <p> to transmit the data between jinja2 and javascript.
    It was awful and disturbing but at least I made it.
    And I think there must be better ways like Ajax and JSON, I'm working on it.
    """
    card = Card.card_or_404(cardid)   # it's a Card
    if current_user.kname != card.data.get('author'):
        flash('Permission Denied')
        return redirect(url_for('main.cardpage', cardid=cardid))
    if request.args.get('private') == '0':
        card.public()
        flash('This card is public now!')
        return redirect(url_for('main.cardpage', cardid=cardid))
    if request.args.get('private') == '1':
        card.private()
        flash('This card is pravite now!')
        return redirect(url_for('main.cardpage', cardid=cardid))
    card = card.data.get('content')  # it's content
    edit_form = WriteForm()
    if edit_form.validate_on_submit():
        Card.edit(cardid, edit_form.content.data)
        flash('Card modified.')
        return redirect(url_for('main.edit', cardid=cardid)) # POST-REDIRECT-GET
    return render_template('card/edit.html', edit_form=edit_form, card=card)


@main.route('/card/delete/<cardid>', methods=['POST', 'GET'])
@login_required
def delete(cardid):
    """
    delele a card, the subcards will all be deleted as well,
    it redirects to the father of the card whether a user or a card
    """
    card = Card.card_or_404(cardid)
    if current_user.kname != card.data.get('author'):
        flash('Permission denied.')
        return redirect(url_for('main.cardpage', cardid=cardid))
    card.delete(_all=True)
    curdadid = card.data.get('dad')
    curdad = User.user_or_none(curdadid)               # not confirmed
    if curdad.data: # person, no need to move
        flash('Card collection deleted')
        return redirect(url_for('main.userpage', username=curdadid))
    flash('Cards deleted')
    return redirect(url_for('main.cardpage', cardid=curdadid))


@main.route('/card/move/<cardid>', methods=['POST', 'GET'])
@login_required
def move(cardid):
    """
    move a card to the higher
    """
    card = Card.card_or_404(cardid)
    if current_user.kname != card.data.get('author'):
        flash('Permission denied.')
        return redirect(url_for('main.cardpage', cardid=cardid))
    # find current father
    curdadid = card.data.get('dad')
    curdad = User.user_or_none(curdadid)               # not confirmed
    curdad = curdad.data.get('kname')
    if curdad: # person, no need to move
        flash("Not moved as in user's root.")
        return redirect(url_for('main.cardpage', cardid=cardid))
    else:
        curdad = Card.card_or_404(curdadid)
    # find the grandpa
    newdadid = curdad.data.get('dad')
    newdad = User.user_or_none(newdadid)               # not confirmed
    newdad = newdad.data.get('kname') or Card.card_or_404(newdadid).data.get('_id')
    # found
    Card.addson(newdad, cardid)                        # notice! update the database
    flash('Card moved.')
    return redirect(url_for('main.cardpage', cardid=cardid))
