import db
import flask
import flask_login
from urllib.parse import urlparse, urljoin

manager = flask_login.LoginManager()



class User():
	def __init__(self, teacher=None):
		self._tid = teacher.id        if teacher else None
		self._name = teacher.name     if teacher else 'User'
		self._user = teacher.username if teacher else None
	#end def

	@property
	def tid(self):
		return self._tid
	#end def

	@property
	def name(self):
		return self._name
	#end def

	@property
	def username(self):
		return self._user
	#end def

	@property
	def is_active(self):
		'''This property should return True if this is an active user
		In addition to being authenticated, they also have activated
		their account, not been suspended, or any condition your
		application has for rejecting an account. Inactive accounts may
		not log in'''
		# return self._active
		return self.is_authenticated
	#end def

	@property
	def is_anonymous(self):
		'''This property should return True if this is an anonymous
		user. Actual users return False.'''
		# return self._is_anonymous
		return not self.is_authenticated
	#end def


	@property
	def is_authenticated(self):
		'''This property should return True if the user is
		authenticated, i.e. they have provided valid credentials.'''
		return self._tid is not None
	#end def


	def get_id(self):
		'''This method must return a str that uniquely identifies this user,
		and can be used to load the user from the user_loader callback'''
		return str(self._user)
	#end def


	@staticmethod
	def login(username, password):
		t = db.fetch_teacher_by_username(username)
		if t.password != password:
			return User(None)
		u = User(t)
		flask_login.login_user(u, remember=True)
		return u
	#end def


	@staticmethod
	def from_username(username):
		t = db.fetch_teacher_by_username(username)
		u = User(t)
		# flask_login.login_user(u, remember=True)
		return u
	#end def
#end class



def login(username, password):
	return User.login(username, password)
#end def



def setup(app):
	manager.init_app(app)
#end def



@manager.user_loader
def load_user(user_id):
	'''Reload the user object from the user ID stored in the session.'''
	# return User.get(user_id)
	return User.from_username(user_id)
#end def



def is_safe_url(target):
	ref_url = urlparse(flask.request.host_url)
	test_url = urlparse(urljoin(flask.request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
			ref_url.netloc == test_url.netloc
#end def
