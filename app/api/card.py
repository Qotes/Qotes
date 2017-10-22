"""
endpoints for cards，alomost all methods on cards are implemented in this file,
including finding subcards of someuser(which means finding cards by author
are not included),

basically the methods on a single card is in URI like `/card/<cardid>',
while the methods affects several cards at one time is in URI like `/cards`,
the tranditional `/card/<cardid>/` and `/cards/` are alse available as alias,

when there could be several cards to return, the data will be divided into
pages, mainly the GET all cards or subcards of a user or card
"""

from flask import jsonify, url_for, request, g, redirect
from . import api
from .errors import bad_request
from .decorators import author_required
from .. import db
from ..models import Card, User, Pagination


@api.route('/card/<cardid>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def card(cardid):
    """methods on a single card itself
    """
    thiscard = Card.card_or_404(cardid)

    def get():
        """returns the information of a card in json
        """
        return jsonify(thiscard.to_json(userfrom=g.current_user.kname))

    @author_required(thiscard)
    def post():
        """post a card as the subcard of the current card, it returns
        a json with `{'author': author, 'content': content}`

        """
        content = request.json.get('content') or ''
        author = g.current_user.kname
        Card(author, content).addto_db(fatherid=cardid)
        return jsonify({'author': author, 'content': content}), 201

    @author_required(thiscard)
    def put():
        """edit a card,
        only input content is fetchable, the content is supposed to
        be written in markdown or converted from html

        :args-addson: add a card to the current card
        """
        newson = request.args.get('addson')
        if newson:
            newson = Card.card_or_404(newson)
            @author_required(newson)
            def addson():
                """check the authentication of subcards"""
                return jsonify(Card.addson(thiscard.data.get('_id'), newson))
            return addson()
        content = request.json.get('content') or ''
        thiscard.edit(cardid, content)
        return jsonify({
            'url': url_for('api.get_card', cardid=cardid, _external=True),
            'content': content
        })

    @author_required(thiscard)
    def delete():
        """delete a card itself,
        subcards of it will be moved to higher if all is not given

        :args-all: delete all the subcards if given
        """
        del_all = request.args.get('all')
        return jsonify(thiscard.delete(_all=del_all))

    implements = {
        'GET': get,
        'POST': post,
        'PUT': put,
        'DELETE': delete,
        None: bad_request
    }

    return implements.get(request.method)()


@api.route('/cards', methods=['GET', 'POST'])
def cards():
    """methods on several cards, create new cards to the user's
    root is also implemented in this function,

    I used the `/cards/` as the uri at first, but I changed it to apply
    the args about methods on subcards
    """
    thesecards = db.card.find()

    def get():
        """returns the information of several cards in json, the cards will be
        paginated and returns the first page on default, the cards are all without
        contents, they are supposed to be viewed in small cards

        :args-sons: returns a list of dicts of subcards of the current card
        :args-page: returns a page of cards, if not given returns the first page
        """
        father = request.args.get('father')
        page = request.args.get('page') or 1
        if father:
            author = User.user_or_none(father).data.get('kname') or Card.card_or_404(father).data.get('author')
            cursor = Card.get_sons(father, g.current_user.kname, author)
        else:
            father = 'root'
            cursor = thesecards
        pagination = Pagination(cursor, page)
        return jsonify({
            'father': father,
            'page': page,
            'pagecounts': pagination.pages_count,
            'prevpage': url_for('api.cards', page=pagination.prev, _external=True),
            'nextpage': url_for('api.cards', page=pagination.next, _external=True),
            'cardcounts': pagination.items_count,
            'cards': [{
                'url': url_for('api.card', cardid=card.data.get('_id'), _external=True),
                'author': url_for('api.user', kname=card.data.get('author'), _external=True), # TODO
                'title': card.data.get('title'),
                'outline': card.data.get('gist'),
                'tags': card.data.get('tags'),
                'timestamp': card.data.get('since'),
                'father': card.data.get('dad'),
            } for card in pagination.page]
        })

    def post():
        """post a card as a new collection, it returns
        a json with `{'author': author, 'content': content}`
        """
        content = request.json.get('content') or ''
        author = g.current_user.kname
        Card(author, content).addto_db()
        return jsonify({'author': author, 'content': content}), 201

    implements = {
        'GET': get,
        'POST': post,
        None: bad_request
    }

    return implements.get(request.method)()


@api.route('/cards/', methods=['GET'])
def all_card():
    """ an alias of get all cards in `/cards/` in GET, thers no method for POST
    as it goes against the theme of `/cards/`
    """
    return redirect(url_for('api.cards', father=request.args.get('father'), page=request.args.get('page')))


@api.route('/cards/<father>/', methods=['GET'])
def get_subcards(father):
    """an alias of get subcards of a card or user in `/cards/cardid/`"""
    return redirect(url_for('api.cards', father=father, page=request.args.get('page')))
