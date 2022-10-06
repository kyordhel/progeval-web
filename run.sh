#!/bin/bash

source env/bin/activate
export FLASK_ENV="development"
export FLASK_APP="$(pwd)/index.wsgi"
python -m flask run --host 0.0.0.0
cd ..
