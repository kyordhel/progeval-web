#!/bin/bash

# Requires libapache2-mod-wsgi-py3

if [ ! -d "env" ]
then
	virtualenv -p python3 env
fi
source env/bin/activate
pip install flask flask-login
pip install -r requirements.txt

chmod g+s .
mkdir -p \
	logs \
	specfiles \
	static/css \
	static/img \
	static/js \
	static/reports \
	templates/admin \
	uploads

PIPATH=$(pip --version | perl -nle 'm/from ([^ ]*)/; print $1')
PIPATH=$(dirname ${PIPATH})
echo "Add the following line to the WSGIDaemonProcess line in the app's apache .conf file"
echo "python-path=$(pwd):${PIPATH}"

deactivate
