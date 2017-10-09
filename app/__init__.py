"""
initital the applicaiotn
"""

from pymongo import MongoClient
from flask import Flask
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from config import config
# for markdownparser
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from bs4 import BeautifulSoup as BS

# renderer-----------------------------------------------------------------------------
class HighlightRenderer(mistune.Renderer):
    """
    There was a problem with highlight as the `<pre>` is not classifed 'highlight',
    I used BeautifulSoup to fix it.
    """
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        soup = BS(highlight(code, lexer, formatter), 'html.parser')
        soup.pre['class'] = 'highlight'
        return str(soup)

renderer = HighlightRenderer()

# configs------------------------------------------------------------------------------
loginmanager = LoginManager()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
# pymongo is not an ODM so it's a bit little different
mongoclient = MongoClient('mongodb://qotes:qotes@127.0.0.1', connect=False)
db = mongoclient.qotes
# specific settings for loginmanager
loginmanager.session_protection = 'strong'
loginmanager.login_view = 'auth.login'          # prepared for login_required
# markdown parser
markdown = mistune.Markdown(renderer=renderer, escape=True, hard_wrap=True)

# register-----------------------------------------------------------------------------
def create_app(config_name):
    """register the extentions
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    loginmanager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
