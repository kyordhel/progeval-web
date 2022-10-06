import os
import sys
here = os.path.dirname(__file__)
sys.path.insert(0, here)

# Path to the virtual environment
activate_this = os.path.join(here, 'env', 'bin', 'activate_this.py')

with open(activate_this, 'r') as f:
    exec(f.read(), dict(__file__=activate_this))

from app import app as application
