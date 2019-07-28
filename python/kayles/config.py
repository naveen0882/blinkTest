import os
import logging

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8000'))
DEBUG = bool(os.environ.get('DEBUG', '1'))
LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG')
