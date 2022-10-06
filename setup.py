import os
import sys
from flask import current_app

HERE   = os.path.dirname(__file__)
if not HERE in sys.path:
    sys.path.insert(0, HERE)
STATIC = os.path.abspath(os.path.join(HERE, "static"))
VENV   = os.path.abspath(os.path.join(HERE, "env"))

UPLOAD_FOLDER = os.path.abspath(os.path.join(HERE, 'uploads'))
SPECSF_FOLDER = os.path.abspath(os.path.join(HERE, 'specfiles'))
REPORT_FOLDER = os.path.abspath(os.path.join(HERE, 'static', 'reports'))

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.exists(SPECSF_FOLDER):
    os.mkdir(SPECSF_FOLDER)
if not os.path.exists(REPORT_FOLDER):
    os.mkdir(REPORT_FOLDER)
