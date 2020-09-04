import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    ADMINS = ['your-email@example.com']
    AUTHY_APP_NAME = os.environ.get('AUTHY_APP_NAME')
    AUTHY_APP_ID = os.environ.get('AUTHY_APP_ID')
    AUTHY_PRODUCTION_API_KEY = os.environ.get('AUTHY_PRODUCTION_API_KEY')
