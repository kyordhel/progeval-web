import os
from setup import HERE
# from flask import current_app, g
from sqlalchemy import Column, ForeignKey, UniqueConstraint, \
                       Boolean, DateTime, Integer, \
                       String, Text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


_app = None
_db = SQLAlchemy()
BaseModel = _db.Model

def setup(app):
	global _app
	# postgresql://username:password@host:port/database_name
	# mysql://username:password@host:port/database_name
	dbpath = os.path.abspath(os.path.join(HERE, 'database.db'))
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	_db.init_app(app)
	_app = app
	if not os.path.isfile(dbpath):
		with app.app_context():
			_db.create_all()
			_db.session.commit()
# end def



def get_db():
	return _db
# end def



class Teacher(BaseModel):
	__tablename__ = "Teachers"

	id        = Column('tchId',    Integer,     primary_key=True)
	name      = Column('tchName',  String(250),              nullable=False)
	username  = Column('username', String(50),  unique=True, nullable=False)
	password  = Column('password', String(50),               nullable=False)

	groups    = relationship('Group', back_populates='teacher')
	# groups    = relationship('Group', backref='teacher', lazy=True)
	# groups    = relationship('Group', primaryjoin='Group.teacherId==Teacher.id')

	def __str__(self):
		return f'{self.name}'
	# end def

	def __repr__(self):
		return f'<Teacher {self.name} | id: {self.id}>'
	# end def
# end class



class Group(BaseModel):
	__tablename__ = "Groups"

	id        = Column('grpId',      Integer, primary_key=True)
	teacherId = Column('tchId',      Integer, ForeignKey('Teachers.tchId'),
													nullable=False)
	subject   = Column('grpSubject', String(250),   nullable=False)
	number    = Column('grpNumber',  Integer,       nullable=False)

	teacher   = relationship('Teacher', back_populates='groups')
	# teacher   = relationship('Teacher', foreign_keys=[teacherId], back_populates='groups')
	evaluators= relationship('Evaluator', back_populates='group')
	# evaluators= relationship('Evaluator', backref='group', lazy=True)

	__table_args__ = (
		UniqueConstraint('tchId', 'grpSubject', 'grpNumber', name='teacher_subject_group_uc'),
	)

	def __str__(self):
		return f'{self.number}'
	# end def

	def __repr__(self):
		return f'<Group {self.subject}-G{self.number} | id: {self.id}>'
	# end def
# end class



class Evaluator(BaseModel):
	__tablename__ = "Evaluators"

	id        = Column(Integer, primary_key=True)
	groupId   = Column(Integer, ForeignKey('Groups.grpId'),
													nullable=False)
	name      = Column(String(250),                 nullable=False)
	file      = Column(Text,                        nullable=False)
	created   = Column(DateTime(timezone=True),
							server_default=func.now())
	active    = Column(Boolean,                     nullable=False)
	expires   = Column(DateTime(timezone=True),     nullable=True)

	group     = relationship('Group', back_populates='evaluators')

	__table_args__ = (
		UniqueConstraint('groupId', 'name', name='group_eval_uc'),
	)

	def __str__(self):
		return f'{self.name}'
	# end def

	def __repr__(self):
		return f'<Evaluator {self.name} | id: {self.id}>'
	# end def
# end class



def fetch_teacher(tid):
	return Teacher.query.get(tid)
#end def



def fetch_teacher_by_username(username):
	return Teacher.query.filter(
		func.lower(Teacher.username) == func.lower(username)
	).first()
#end def



def fetch_group(gid):
	# return db.Group.query.get_or_404()
	# return db.Group.query.filter_by(id=gid).first()
	return Group.query.get(gid)
#end def



def fetch_groups(tid=None):
	# if tid:
	# 	groups = Group.query.order_by(
	# 		Group.subject,
	# 		Group.number
	# 	).filter(Group.teacherId == tid).all()
	# else:
	# 	groups = Group.query.order_by(
	# 		Group.subject,
	# 		Group.number
	# 	).all()
	# return groups
	groups = Group.query
	if tid:
		groups = groups.filter(Group.teacherId == tid)
	return groups.order_by(
			Group.subject,
			Group.number
		).all()
#end def



def fetch_groups_we():
	groups = Group.query\
		.filter(
			Group.evaluators.any(Evaluator.active)
		)\
		.order_by(
			Group.subject,
			Group.number
		).all()
	return groups
#end def



def fetch_evaluator(eid):
	return Evaluator.query.get(eid)
#end def



def fetch_evaluators(tid):
	return Evaluator.query\
		.join(Evaluator.group)\
		.join(Group.teacher)\
		.filter(
			Teacher.id==tid
		)\
		.order_by(
			Group.subject,
			Group.number,
			Evaluator.created
		)\
		.all()
#end def