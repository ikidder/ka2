from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from ka.models import User
from ka.database import Session


class RegistrationForm(FlaskForm):
    name = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_name(self, field):
        user = Session.query(User).filter_by(name=field.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

        if '_' in field.data:
            raise ValidationError('Underscores are not allowed in titles.')

    def validate_email(self, field):
        user = Session.query(User).filter_by(email=field.data).first()
        if user:
            raise ValidationError('Unable to process that email address. Please choose a different one.')


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
            user = Session.query(User).filter_by(email=email.data).first()
            if user:
                raise ValidationError('Please choose a different email.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')