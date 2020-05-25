from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from khds_form.models import User

class LoginForm(FlaskForm):
	flat = StringField('Flat No.', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

class RegisterationForm(FlaskForm):
	flat = StringField('Flat No.', validators=[DataRequired(), Length(min=2, max=20)])
	name = StringField('Member Name:', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Sorry this username is taken, Please choose another one')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Sorry this email is taken, Please choose another one')

class RequestLinkForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ConsentForm(FlaskForm):
	name = StringField('Member Name:', validators=[DataRequired()])
	flat = StringField('Flat No.', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	zoom_meeting = StringField('Should the GBM and Election of New Management Committee held over a Zoom Conferencing ?', validators=[DataRequired()])
	submit = SubmitField('Submit')