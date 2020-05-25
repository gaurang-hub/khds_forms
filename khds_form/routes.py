import os
import secrets
from datetime import datetime
from pytz import timezone
from flask import render_template, redirect, url_for, flash, request
from khds_form import app, bcrypt, db, mail
from khds_form.forms import LoginForm, RegisterationForm, RequestLinkForm, ConsentForm
from khds_form.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
@login_required
def home():
	return render_template('home.html', title='Home')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(flat=form.flat.data, email=form.email.data, password=hashed_password, name=form.name.data)
		db.session.add(user)
		db.session.commit()
		flash('Your Account Has Been Successfully Created. Now you can Log In', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('request_link'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(flat=form.flat.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')			
			return redirect(next_page) if next_page else redirect(url_for('request_link'))
		else:
			flash('Login Unsuccessful, Please check your email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))

def send_form_email(user):
    token = user.get_form_token()
    msg = Message('KHDS Consent Form Link',
                  sender='contactkhds@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/request_link", methods=['GET', 'POST'])
@login_required
def request_link():
	if current_user.form_submitted == 1:
		flash('Your Response has been recorded. Thank You!', 'info')
		return redirect(url_for('logout'))
	form = RequestLinkForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_form_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.email.data = current_user.email
	return render_template('link_request.html', title='Request Link', form=form)

def send_response_email(user):
	email = 'ga.sh.ak47@gmail.com'
	msg = Message(f'KHDS Consent Form Response of {user.name}', sender='contactkhds@gmail.com', recipients=email.split())
	msg.body = f'''Member Name: {user.name}
Email: {user.email}
Flat No.: {user.flat}
Should the GBM and Election of New Management Committee held over a Zoom Conferencing?
{user.zoom_meeting}
Date and Time Responded: {user.date_responded}
'''
	mail.send(msg)


@app.route("/consent_form/<token>", methods=['GET', 'POST'])
def reset_token(token):
	user = User.verify_form_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('request_link'))
	form = ConsentForm()
	if form.validate_on_submit():
		user.zoom_meeting = form.zoom_meeting.data
		user.date_responded = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
		user.form_submitted = 1
		db.session.commit()
		send_response_email(user)
		flash('Your response has been recorded.', 'success')
		return redirect(url_for('logout'))
	elif request.method == 'GET':
		form.email.data = current_user.email
		form.name.data = current_user.name
		form.flat.data = current_user.flat
	return render_template('consent_form.html', title='Consent Form', form=form)

