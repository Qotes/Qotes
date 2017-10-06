"""
endpoints for cards，

TODO requests for cards' pagenations
"""

from flask import jsonify, url_for, request, g
from . import api
from.errors import forbidden
from .. import db
from ..models import Card


@api.route('/cards/')
def get_cards():
    """get all cards"""
    cards = db.card.find()
    return jsonify(
        {'cards': [Card(data=card).to_json() for card in cards]}
    )


@api.route('/cards/', methods=['POST'])
def post():
    """post a card, it returns a json with
    `{'author': author, 'content': content}`
    """
    content = request.json.get('content') or ''
    author = g.current_user.kname
    card = Card(author, content)
    card.addto_db()                 # notice! insert into the db
    return jsonify({'author': author, 'content': content}), 201

@api.route('/card/<cardid>')
def get_card(cardid):
    """get a card by id"""
    card = Card.card_or_404(cardid)
    return jsonify(card.to_json())


@api.route('/card/<cardid>', methods=['PUT'])
def edit_card(cardid):
    """edit a card,
    only input content is fetchable, the content is supposed to
    be written in markdown or converted from html
    """
    card = Card.card_or_404(cardid)
    author = card.data.get('author')
    if g.current_user.kname != author:
        return forbidden('Not the author of the card.')
    content = request.json.get('content') or ''
    card.edit(cardid, content)
    return jsonify({
        'card': url_for('api.get_card', cardid=cardid, _external=True),
        'content': content
    })


@api.route('/card/<cardid>', methods=['DELETE'])
def delete_card(cardid):
    """
    delete a card,
    subcards of it will be moved to higher
    """
    card = Card.card_or_404(cardid)
    author = card.data.get('author')
    if g.current_user.kname != author:
        return forbidden('Not the author of the card.')
    result = card.delete()
    return jsonify(result)

@api.route('/card/<cardid>/')
def get_card_sons(cardid):
    """
    get a card's subcards by id

    the cards found by query are dicts so I have
    to convert them to instances
    """
    cards = db.card.find({'dad': cardid})
    return jsonify({
        'card': url_for('api.get_card', cardid=cardid, _external=True),
        'subcards': [Card(data=card).to_json() for card in cards],
    })


@api.route('/card/<cardid>/', methods=['DELETE'])
def delete_cards(cardid):
    """
    delete a card,
    subcards of it will be deleted as well
    """
    card = Card.card_or_404(cardid)
    author = card.data.get('author')
    if g.current_user.kname != author:
        return forbidden('Not the author of the card.')
    result = card.delete(_all=True)
    return jsonify(result)


@api.route('/card/<father>/<son>', methods=['PUT'])
def addson(father, son):
    """
    add a card to anther by api
    """
    author = Card.card_or_404(father).data.get('author')
    if g.current_user.kname != author:
        return forbidden('Not the author of the card.')
    author = Card.card_or_404(son).data.get('author')
    if g.current_user.kname != author:
        return forbidden('Not the author of the card.')
    Card.addson(father, son)            # notice! update database
    return jsonify({'card': father, 'subcard': son})
