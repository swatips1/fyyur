import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# DATABASE URL and Config
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Aspen100@localhost:5432/fire1'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# For validation
WTF_CSRF_TIME_LIMIT = None
WTF_CSRF_CHECK_DEFAULT =False
SECRET_KEY = 'you-will-never-guess'
CSRF_SESSION_KEY = 'my-key'
