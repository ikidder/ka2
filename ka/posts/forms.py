from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Content', validators=[DataRequired()])


class DeletePostForm(FlaskForm):
    delete = HiddenField('Delete')