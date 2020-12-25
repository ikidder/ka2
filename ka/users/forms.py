from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from sqlalchemy import func
from ka.models import User
from ka import db


class RegistrationForm(FlaskForm):
    name = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    over_eighteen = BooleanField("I'm over 18.")
    token = HiddenField()
    #password = PasswordField('Password', validators=[DataRequired()])
    #confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_name(self, field):
        user = User.query.filter(func.lower(User.name) == func.lower(field.data)).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

        if '_' in field.data:
            raise ValidationError('Underscores are not allowed in names.')
        if field.data.startswith('&'):
            raise ValidationError("The first character of a name cannot be a '&'")

    def validate_email(self, field):
        user = User.query.filter(func.lower(User.email) == func.lower(field.data)).first()
        if user:
            raise ValidationError('Unable to process that email address. Please choose a different one.')

    def validate_over_eighteen(self, field):
        if not field.data:
            raise ValidationError('You must be 18 years old, or older, to use this service.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    text = TextAreaField('Profile (optional)', validators=[Length(max=1000)])
    
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Please choose a different email.')

    def validate_text(self, field):
        if '<script' in field.data:
            raise ValidationError('Please see https://youtu.be/dQw4w9WgXcQ!')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class SendInvite(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Send Invite')

    def validate_email(self, email):
        if ';' in email.data:
            raise ValidationError('Semicolons are not allowed. Please send one invitation at a time.')


class UnsubscribeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Unsubscribe')

