from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, ValidationError
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Content', validators=[DataRequired()])

    def validate_name(self, field):
        if '_' in field.data:
            raise ValidationError('Underscores are not allowed in titles.')
        if field.data.startswith('&'):
            raise ValidationError("The first character of a title cannot be a '&'")


class DeletePostForm(FlaskForm):
    delete = HiddenField('Delete')