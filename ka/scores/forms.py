from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField, ValidationError
from wtforms.validators import DataRequired
from ka.models import tempos, dynamics, for_players, Score, Measure, ForPlayers

fp_names = [fp.name for fp in for_players]
fp_values = [fp.value for fp in for_players]


class ScoreForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Description', validators=[DataRequired()])
    for_players = SelectField(u'For Players', choices=list(zip(fp_names, fp_values)), default='for any two lovers')

    def validate_name(self, field):
        if '_' in field.data:
            raise ValidationError('Underscores are not allowed in titles.')
        if field.data.startswith('&'):
            raise ValidationError("The first character of a title cannot be a '&'")


class DeleteScoreForm(FlaskForm):
    delete = HiddenField('Delete')


duration_choices = [
    (15, '15 seconds'),
    (30, '30 seconds'),
    (45, '45 seconds'),
    (60, '1 minute'),
    (120, '2 minutes'),
    (180, '3 minutes'),
    (300, '5 minutes'),
    (480, '8 minutes'),
]

tempo_values = [tempo.value for tempo in tempos]
dynamic_values = [dynamic.value for dynamic in dynamics]


class MeasureForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired()])
    tempo = SelectField('Tempo', choices=list(zip(tempo_values, tempo_values)), default='Moderato')
    dynamic = SelectField(u'Dynamic', choices=list(zip(dynamic_values, dynamic_values)), default='Piano')
    text = TextAreaField('Description', validators=[DataRequired()])
    duration = IntegerField('Duration (in seconds)', validators=[DataRequired()], default=45)

    def validate_name(self, field):
        if '_' in field.data:
            raise ValidationError('Underscores are not allowed in titles.')

class DeleteMeasureForm(FlaskForm):
    delete = HiddenField('Delete')