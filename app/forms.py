from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField, SelectMultipleField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.models import User
# from wtforms_sqlalchemy.fields import QuerySelectField

class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """
    def pre_validate(self, form):
        pass

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

class CreateDiscussionForm(FlaskForm):
    theme = StringField('Theme of your topic',validators=[DataRequired(message='This area is required'),
                                            Length(min=20, max=150, message='Theme of topic must be in range from 20 to 150 characters')])
    text = TextAreaField('Your entire question or something else must be here', validators=[DataRequired(message='This area is required'),
                                            Length(min=30, max=10000,message='Description of topic must be in range from 50 to 10 000 characters' )])
    # theme id
    theme_id = HiddenField(validators=[DataRequired()])

    """
    Since choices array are empty in class definition, and generates in certain controller dynamically,
    validation method compares empty choices and generated choices and raises not valid choice exception.
    NonValidatingSelectMultipleField overrides SelectMultipleField validate method, and make possibility to pass through empty choices array without exception.
    """
    tags = NonValidatingSelectMultipleField('Add a couple tags according to you theme', choices=[], coerce=int)
    submit = SubmitField('Create')

class CreateCommentForm(FlaskForm):
    text = TextAreaField('You can leave comment here', validators=[DataRequired(message='This area is required'),
                                            Length(min=2, max=500,message='Comment must be in range from 2 to 500 characters' )])
    submit = SubmitField('Leave comment')