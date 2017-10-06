"""
Since I changed the mongoengine to **pymongo**, the model of User
was supposed to be much simpler. But I found it impossible later.
I have to enlarge the frame to complete some functions that would
be quoted frequently.

It was only designed to cooperate with flask_login, and the the only
useful variable is a unique attribute.It can be kname or email, I
chosed kname. But later I have to enlarge it by giving it an attribute
called data for empty as default.

For MongoDB's sake it's really convenient that you don't have to reframe
the database or collections or tables when you want to change the model
to implement some new functions.

The Permission and Pagination is also included in this file.
"""

from datetime import datetime
# for card
import bleach
from bs4 import BeautifulSoup as BS
from bson.objectid import ObjectId
from bson.errors import InvalidId
# from tomd import Tomd
# for user
from flask import current_app, abort, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as JWS
from itsdangerous import BadSignature
from werkzeug.security import generate_password_hash as gen_hash
from werkzeug.security import check_password_hash as chk_hash
from . import db, loginmanager, markdown


class User(UserMixin):
    """
    It's mostly used to work with flask_login.
    Try not to use user.email or user.pdhs,
    use user.kname to identify.

    If there're needs to use user's information,
    just directly use a query, it should be like
    ```
    user = db.user.find_one({'kname': somename}) # it's a dict
    email = user.get('email')
    follers = user.get('folers')
    ```
    In this way, query the database for one time.

    Or you can do it like this:
    ```
    user = User.user_or_none(somename) #it's a User with data
    email = user.data.get('email')
    ```
    """
    def __init__(self, kname, data=None):
        self.kname = kname
        self.data = data

    def addto_db(self, email, password):
        """
        insert a new user from form into the database
        """
        new_user = {
            # basic information from form
            'email': email,                    # main email
            'kname': self.kname,               # nickname - the most important
            'pdhs': gen_hash(password),        # password hash
            # more defaut information
            'aboutme': 'Lazy guy.',            # moreinformation
            'since': datetime.utcnow(),        # registered since
            'lastseen': datetime.utcnow(),     # login touch
            'tags': [],                        # tags of cards TODO
            'folers': [],                      # followers
            'foling': ['sy'],                  # following
            'cfm': False,                      # register confirm
            'oauth': [],                       # information
            'avatar': 'http://upload-images.jianshu.io/upload_images/6093544-2fff8c19da2e2f35.jpg',
            'pms': Permission.roles['USER']    # permission for default
        }
        db.user.insert_one(new_user)         # notice! insert into database

    @property
    def pdhs(self):
        """return the password hash of the user
        """
        return db.user.find_one({'kname':self.kname}).get('pdhs')

    @property
    def email(self):
        """Tracks the email of a user by kname
        """
        return db.sser.find_one({'kname':self.kname}).get('email')

    def get_id(self):
        """
        To override the UserMixin defaults. It returns the kname of the user.

        I'm considering replacing it with `self.data.get('_id')` since I've
        changed the loginmanager.user_loader. But since then it works.
        """
        return self.kname      # maybe self.data.get('_id') is better

    def gen_reg_token(self):
        """
        Generate the token to confirm registering,
        timeout 1800s
        """
        jws_key = JWS(current_app.config['SECRET_KEY'], 1800)
        return jws_key.dumps({'confirm': self.kname})

    def chk_reg_token(self, token):
        """
        The exceptions may need more tests,
        but since then I'vent found any exceptions.
        """
        jws_key = JWS(current_app.config['SECRET_KEY'])
        try:
            data = jws_key.loads(token)
        except BadSignature:
            return False
        if data.get('confirm') != self.kname:
            return False
        return True

    @staticmethod
    def chk_password(pdhs, password):
        """
        Basically a wrapped `check_password_hash`, but works as
        a staticmethod.

        Check the password,
        return a `True` if the password matched,
        `False` otherwise
        """
        return chk_hash(pdhs, password)

    def ping(self):
        """update the timestamp of logging.
        **NOTICE!** update the database
        """
        db.user.update_one(
            {'kname': self.kname},
            {'$set': {'lastseen': datetime.utcnow()}}
        )

    @staticmethod
    def user_or_none(kname=None, email=None):
        """If username in use, it returns a User, else returns a
        **fake user** with `{}` as data.
        Just call this method `User.user_or_none(somename)`

        It's also capable of finding a user by email.It has to be callled
        in this way:`User.user_or_none(email=someemail)`

        This makes the query like
        `db.user.find_one({'kname':kname})['cfm']`much safer.
        """
        if kname:
            data = db.user.find_one({'kname': kname})
            data = data or {}
            return User(kname=kname, data=data)
        if email:
            data = db.user.find_one({'email': email})
            data = data or {}
            return User(kname=data.get('kname'), data=data)
        abort(500)

    def gen_api_token(self):
        """
        Generates the token for api request.It works for a week.

        Note that use the **kname** to identify.
        """
        jws_key = JWS(current_app.config['SECRET_KEY'], expires_in=604800)
        return jws_key.dumps({'kname': self.kname})

    @staticmethod
    def chk_api_token(token):
        """
        check the token for api,
        it returns a User with data, if user not verified,
        the data will be an empty dictionary {}
        """
        jws_key = JWS(token)
        try:
            data = jws_key.loads(token)
        except BadSignature:
            return User('who?', {})
        return User.user_or_none(data.get('kname'))

    def to_json(self):
        """
        This method is supposed to be called by user found by
        `user_or_none()` which means it is a User with data.
        """
        data = self.data or {}             # {} is just for safety
        json_user = {
            'url': url_for('api.get_user', kname=self.kname, _external=True),
            'username': self.kname,
            'member_since': data.get('since'),
            'last_seen': data.get('lastseen'),
            # avator
            'aboutme': data.get('aboutme'),
            'tags': data.get('tags'),
            'cards': [card.get('_id') for card in db.card.find({'dad': self.kname})],
            'follers': data.get('folers'),
            'follering': data.get('foling')
        }
        return json_user

    def can(self, action):
        """
        the user is supposed to be with data to fetch the role information,
        modify the permission of a action
        """
        permission = self.data.get('pms') or Permission.roles.get('ANONY')
        return (permission & action) == action


class AnonymousUser(AnonymousUserMixin):
    """Anonymous has a kname called 'dr.who', it also overides the `get_id`
    function to cooperate the loginmanager
    """
    @property
    def kname(self):
        """default kname for anonymous user"""
        return 'dr.who'

    def get_id(self):
        """to work with the loginmanager"""
        return self.kname

    def can(self, action):
        """anonymous user can only read cards for defualt"""
        permission = Permission.roles.get('ANONY')
        return (permission & action) == action

    def is_administrator(self):
        """actually not needed right now"""
        return False


loginmanager.anonymous_user = AnonymousUser


@loginmanager.user_loader
def load_user(kname):
    """
    Return a **fake user** to keep loaded.
    But it is exactly the same as the user logged in,
    so, there's no differences.

    It reports some problems if you use current_user's attributes
    like  current_user.data, it's unsafe coz it reloads a user without
    it's data.
    """
    user = User.user_or_none(kname)
    if not user.data:
        return AnonymousUser()
    return user


# ---------------------------------------------------------------------------


class Permission(object):
    """
    describe the permissions with a 8bit binary number
    0b-0-0-0-0-0-0-0-0-0

    admin-0-editall-readall-read-edit-write-follow,

    This is basically what I use to constrain the users to aviod
    the problems brought by local issues.

    But from now it's actually not working as I directly checked the
    identity of the user in `view.py`. I constrain the user's abilities
    of visiting other users, then they have no ways to fetch their cards.
    """
    FOLLOW = 0x01
    WRITE = 0x02
    EDIT = 0x04
    READ = 0x08
    READ_ALL = 0x10
    EDIT_ALL = 0x20
    ADMIN = 0x80

    roles = {
        'ADMIN': 0xff,                                 # me
        'ANONY': READ,
        'USRE': READ|WRITE|EDIT|FOLLOW,                # default
        'SUPER': READ|WRITE|EDIT|FOLLOW|READ_ALL,      # special users
    }

# ********************************************************************************************** #
# ----------------------------------------user ends--------------------------------------------- #
# ********************************************************************************************** #
# --------------------------------------card is below------------------------------------------- #
# ********************************************************************************************** #


class Card(object):
    """the card model,
    actually there's no need to draw a class like this,
    but I want it to work with User.

    TODO flask_signal automatically change content to html
    """
    def __init__(self, author=None, content='', _id=None, data=None):
        self.author = author
        self.content = content
        self._id = ObjectId(_id)
        self.data = data

    def addto_db(self, fatherid=None):
        """inserts the new card to the db when form submitted, if father
        is given, it inserts the card as its subcard
        NOTICE! this method needs author and content
        """
        html_text = self.bleach_html(markdown(self.content))
        new_card = {
            # basic information from form
            'author': self.author,
            'content': self.content,                  # markdown input
            # more information
            'title': self.gen_title(html_text),       # extract from h1
            'gist': self.gen_gist(html_text),         # extract from h2
            'dad': fatherid or self.author,           # auto find dad
            'since': datetime.utcnow(),               # initial timestamp
            'lastedit': datetime.utcnow(),            # timestamp of editing
            'tags': [],                               # TODO inter author
            'poster':'',                              # TODO optional image
        }
        db.card.insert_one(new_card)                  # notice! insert into database

    @property
    def html(self):
        """
        it's only fetchable when Card is with data
        """
        return self.bleach_html(markdown(self.data.get('content')))

    @staticmethod
    def gen_title(html):
        """
        Generate the h1 by BeautifulSoup.
        If nothing found, it returns a default title.
        """
        if BS(html, 'html.parser').h1:
            return BS(html, 'html.parser').h1.contents[0]
        return 'THIS IS NOT A TITLE'

    @staticmethod
    def gen_gist(html):
        """
        Generate the h2 by BeautifulSoup.
        If nothing found, it returns a default list.
        """
        gened_gist = ['THIS IS NOT A GIST']
        if BS(html, 'html.parser').h2:
            gened_gist = []
            for h2_tag in BS(html, 'html.parser').select('h2'):
                gened_gist.append(h2_tag.get_text())
        return gened_gist

    def add_tags(self):
        """TODO
        """
        pass

    @staticmethod
    def bleach_html(html_text):
        """Clean the html content,
        bleach the html, clean and linklfy.
        """
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p', 'img', 'br', 'span'
        ]
        allowed_attrs = {
            '*': ['class', 'style'],
            'a': ['href', 'rel'],
            'abbr': ['title'],
            'acronym': ['title'],
            'pre': ['lang'],
            'img': ['src', 'alt']                    # NOTICE! INSECURE TODO
        }
        return bleach.linkify(
            bleach.clean(
                html_text,
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=True
            )
        )

    @staticmethod
    def edit(cardid, text, is_html=False):
        """
        Something need to be done when a card is updated,
        it can get both markdown(default) and html texts as input.

        I blocked the simple edit so the second section is not used
        right now.
        """
        if not db.card.find_one({'_id': ObjectId(cardid)}):
            abort(404)
        if is_html is False:
            html_text = markdown(text)                     # turn to html
            html_text = Card.bleach_html(html_text)              # bleach
            db.card.update_one(
                {'_id': ObjectId(cardid)},
                {'$set': {
                    'content': text,
                    'lastedit': datetime.utcnow(),
                    'title': Card.gen_title(html_text),
                    'gist':Card.gen_gist(html_text)
                }}
            )                                     # notice! update the database
        else: # almost blocked
            text = Card.bleach_html(text)                   # bleach
            # text = Tomd(text).markdown            # turn to markdown
            db.card.update_one(
                {'_id': ObjectId(cardid)},
                {'$set': {
                    'content': text,
                    'lastedit': datetime.utcnow(),
                    'title': Card.gen_title(text),
                    'gist':Card.gen_gist(text)
                }}
            )                                    # notice! update the database

    @staticmethod
    def card_or_404(cardid):
        """
        find a card by _id,
        return a Card with Objectid and data
        """
        try:
            objid = ObjectId(cardid)
        except InvalidId:
            abort(404)
        data = db.card.find_one({'_id': objid})
        if not data:
            abort(404)
        return Card(_id=cardid, data=data)

    def to_json(self):
        """
        This method is supposed to be called by card found by
        `card_or_404()` which means it is a Card with data.
        """
        data = self.data or {}             # {} is just for safety
        json_card = {
            'url': url_for('api.get_card', cardid=data.get('_id'), _external=True),
            'author': url_for('api.get_user', kname=data.get('author'), _external=True),
            'title': data.get('title'),
            'outline': data.get('gist'),
            'tags': data.get('tags'),
            'timestamp': data.get('since'),
            'content': data.get('content'),
            'father': data.get('dad'),
            'sons': [card.get('_id') for card in db.card.find({'dad': data.get('_id')})]
        }
        return json_card

    @staticmethod
    def addson(father, son):
        """
        add a card to anther, if there's something wrong, nothing will be done
        """
        if father and son and father != son:            # notice! update database
            db.card.update_one({'_id': ObjectId(son)}, {'$set': {'dad': father}})

    def delete(self, cardid=None, _all=False):
        """
        delete a card,

        If `cardid` is not given, the card must be with data.
        If `_all` is not given, the subcards will be moved to the higher,
        or all its subcards will be deleted as well.

        It returns a dict like `{'card': result, 'subcards': result}`
        """
        if cardid is None:
            try:
                cardid = self.data.get('_id')
            except AttributeError:
                abort(500)
        if _all is False:
            # move the sons to their grandpa
            grandpa = db.card.find_one({'_id': ObjectId(cardid)}).get('dad')
            result = db.card.update_many(
                {'dad': cardid},
                {'$set': {'dad': grandpa}}
            )
            result = result.raw_result
        else:
            # delete all the subcards
            result = db.card.delete_many({'dad': cardid})
            result = result.raw_result
        # delete the objected card
        result_dad = db.card.delete_one({'_id':ObjectId(cardid)})
        return {'card': result_dad, 'subcards': result}

    @property
    def siblings(self):
        """returns a cursor of the siblings,
        the card is supposed to be with data,
        it returns only twenty siblings as result.
        """
        cursor = db.card.find({'dad': self.data.get('dad')}).limit(20)
        return cursor


# ------------------------------------------------------------------------------------------------


class Pagination(object):
    """
    pagination for users or cards, the users or cards would better
    be sorted by id or date or whatever.

    Note that the cursor will not be executed, which means you don't
    have to refresh the cursor after every method. All items are
    cursors as well and they won't leak.

    ```
    cursor = db.collection.find(somethingyoudo)
    pagination = Pagination(cursor, current_page)
    # [current_page items]
    page = pagenation.page     # recommended
    # or it should be
    # [[page1items], [page2items] ...]
    pages = pagination.pages    # deprecated
    page = pages[current_page - 1]
    ```
    """
    def __init__(self, cursor, current_page=1, per=25, outrange=0):
        self.cursor = cursor             # remember not to pollute the cursor
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1
        self.current_page = current_page if current_page > 0 else 1
        self.per = per
        self.items_count = cursor.count()
        self.outrange = self.items_count // self.per
        self.limited = False
        # check the range
        if outrange != 0 and self.outrange > outrange:
            self.outrange = outrange
            self.limited = True            # range is set
        self.pages_count = self.outrange if self.limited else self.outrange + 1

    @property
    def pages(self):
        """
        returns the items of all pages,
        `[page1items, page2items, ...]`
        """
        result = []
        for page in range(1, self.outrange + 1):
            start = (page - 1) * self.per
            end = page * self.per - 1
            result.append(self.cursor[start:end])
        # if limited, exit
        if self.limited:
            return result
        # deals with the last page
        ends = self.outrange * self.per
        ends = self.cursor[ends: self.items_count]
        result.append(ends)
        return result

    @property
    def pages_index(self):
        """
        returns the index for the result of all pages,
        `[(pg1head, pg1tail), (pg2head, pg2tail) ...]`
        """
        result = []
        for page in range(1, self.outrange + 1):
            start = (page - 1) * self.per
            end = page * self.per
            result.append((start, end))
        # if limited, exit
        if self.limited:
            return result
        # deals with the last page
        ends = self.outrange * self.per
        ends = (ends, self.items_count)
        result.append(ends)
        return result

    @property
    def has_prev(self):
        """whether the first page"""
        return self.current_page != 1

    @property
    def prev(self):
        """the previous page"""
        return self.current_page - 1 if self.has_prev else 1

    @property
    def has_next(self):
        """whether the last page"""
        return self.current_page != self.pages_count

    @property
    def next(self):
        """the next page
        there's no need to worry about page outranged as it will keep
        at the last page.
        """
        return self.current_page + 1

    def page_items(self, page=0):
        """
        returns the list of the items for a page，
        if the given page is outranged it returns the last page,
        or if it's not given it returns the current page
        """
        if page == 0:
            page = self.current_page
        if page > self.outrange:    # deals with the last page or outranged pages
            page_index = self.pages_index[self.outrange]
            page_items = self.cursor[page_index[0]: page_index[1]]
            return page_items
        start = (page - 1) * self.per
        end = page * self.per
        page_items = self.cursor[start: end]
        return page_items

    @property
    def page(self):
        """returns current page's items"""
        return self.page_items()

    def pagination(self, edge_prev=2, cur_prev=1, cur_next=3, edge_next=2):
        """
        pagination of pages, it works like`left None cprev
        current cnext None right`

        e.g.:`[1, 2, None, 6, 7, 8, 9, 10, None, 20, 21]`
        """
        left = edge_prev + cur_prev
        right = edge_next + cur_next
        span = left + right + 3        # two None and cur itself
        cur = self.current_page
        total = self.pages_count
        result = []
        # too short
        if total < span:
            return [i + 1 for i in range(total)]
        # left
        if cur <= left + 1:
            result += [i + 1 for i in range(span - edge_next - 1)]
        else:
            result += [i + 1 for i in range(edge_prev)]
            result.append(None)
        # middle
        if left + 1 < cur < total - right:
            result += [cur - cur_prev + i for i in range(cur_prev + 1 + cur_next)]
        # right
        if cur >= total - right:
            result += [total - i for i in range(span - edge_prev - 1)][::-1]
        else:
            result.append(None)
            result += [total - edge_next + i for i in range(edge_next)]
        return result
