import os
import sys
from flask import current_app

HERE   = os.path.abspath(os.path.dirname(__file__))
if not HERE in sys.path:
    sys.path.insert(0, HERE)
STATIC = os.path.join(HERE, "static")
VENV   = os.path.join(HERE, "env")

UPLOAD_FOLDER = os.path.join(HERE, 'uploads')
SPECSF_FOLDER = os.path.join(HERE, 'specfiles')
REPORT_FOLDER = os.path.join(HERE, 'static', 'reports')

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.exists(SPECSF_FOLDER):
    os.mkdir(SPECSF_FOLDER)
if not os.path.exists(REPORT_FOLDER):
    os.mkdir(REPORT_FOLDER)

def set_secret_key(app):
	spath = os.path.join(HERE, 'secret.hex')
	if not os.path.exists(spath):
		import hashlib, time
		sha1 = hashlib.sha1()
		sha1.update('Progeval' + str(time.time()))
		with open(spath, 'w') as f:
			f.write(sha1.hexdigest())
			f.write('\n')
	with open(spath, 'r') as f:
		app.secret_key = f.read().strip()
#end def