"""
docstr
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import Required, Length


class WriteForm(FlaskForm):
    """
    post a new card in two panels
    """
    content = TextAreaField('Post something here.', validators=[Required(), Length(1, 10000)])
    submit = SubmitField('Submit')  # this kind of thing is unneeded


class EditAboutmeForm(FlaskForm):
    """
    it might only be used in userpage
    """
    aboutme = TextAreaField(validators=[Required(), Length(1, 63)])
    submit = SubmitField('Submit')


class QuickCardForm(FlaskForm):
    """
    For quick drawing or editing a existed card.

    It's hidden and get data from an editable div rendered by
    MarkdownIME.
    """
    content = StringField(validators=[Required(), Length(1, 10000)])
    submit = SubmitField('Submit')
