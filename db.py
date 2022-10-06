import os
from setup import HERE
# from flask import current_app, g
from sqlalchemy import Column, ForeignKey, Boolean, DateTime, Integer, \
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



def get_db():
	return _db

"""
CREATE TABLE Evaluators (
	evlId      INTEGER PRIMARY KEY AUTOINCREMENT,
	grpId      INTEGER NOT NULL,
	evlName    TEXT NOT NULL,
	evlFile    TEXT NOT NULL,
	evlCreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	evlActive  BOOLEAN NOT NULL DEFAULT TRUE,
	evlExpires TIMESTAMP DEFAULT NULL,
	FOREIGN KEY (grpId) REFERENCES Groups (grpId)
);
"""
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
	evaluators= relationship('Evaluator', backref='group', lazy=True)

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

	def __str__(self):
		return f'{self.name}'
	# end def

	def __repr__(self):
		return f'<Evaluator {self.name} | id: {self.id}>'
	# end def
# end class

# def close_db(e=None):
# 	db = g.pop('db', None)
# 	if db is not None:
# 		db.close()



# def create_db():
# 	db = get_db()
# 	with open('schema.sql', 'r') as f:
# 		db.executescript(f.read.decode('utf-8'))
