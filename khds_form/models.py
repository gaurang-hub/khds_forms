from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from pytz import timezone
from khds_form import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): 
	id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
	name =  db.Column(db.String(50), nullable=False)
	flat = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	zoom_meeting = db.Column(db.String(10))
	date_responded = db.Column(db.DateTime, default=datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata')), nullable=False)
	form_submitted = db.Column(db.Integer, default=0)

	def get_form_token(self, expires_sec=180):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_form_token(token):
		s=Serializer(app.config['SECRET_KEY'])
		try:
			user_id=s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.flat}', '{self.email}'), '{self.name}', '{self.date_responded}', '{self.zoom_meeting}' "