from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


class EditProfileForm(FlaskForm):
    pic = HiddenField('pic')
    username = StringField('Custom Domain', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    firstName = StringField('FirstName', validators=[DataRequired()])
    lastName = StringField('LastName', validators=[DataRequired()])
    about_me = TextAreaField('About me',
                             validators=[Length(min=0, max=140)])
    availability = TextAreaField('Availability', validators=[Length(min=0, max=140)])
    location = StringField('Location', validators=[Length(min=0, max=140)])
    skills = TextAreaField('Skills', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class CareRequestForm(FlaskForm):
    careType = SelectField(
        'What type of care do you need?',
        choices=[('elderly', 'Elderly Care'), ('child', 'Child Care'), ('pet', 'Pet Care')]
    )
    location = StringField('Location', validators=[DataRequired()])
    careFrequency = SelectField(
        'When do you need care?',
        choices=[('rare', 'Occasional back-up care'), ('ft', 'Full-Time'), ('pt', 'Part Time')]
    )
    needs = TextAreaField('Describe your needs', validators=[Length(min=0, max=200)])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Send Message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

