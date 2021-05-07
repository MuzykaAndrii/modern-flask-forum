from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.models import User

class RegistrationForm(FlaskForm):
    nickname = StringField('nickname', validators=[Length(min=4, max=25, 
                            message='nickname length must be in range from 4 to 25 characters'),
                            DataRequired(message='This area is required'), Regexp('[A-Za-z][A-Za-z0-9_.]*$', 0, 'Unexpected charachter in nickname')])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[Length(min=6, 
                            message='Password should be bigger than 6 characters'), 
                            DataRequired(message='This area is required')])

    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(message='This area is required'), 
                            EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('nickname already in use.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddPhotoForm(FlaskForm):
    picture = FileField('Add product picture', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')