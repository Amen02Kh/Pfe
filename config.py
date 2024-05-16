import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    UPLOAD_EXTENSIONS=['.txt']
    UPLOAD_PATH='uploads'
    UPLOAD_FOLDER=os.path.join(os.getcwd(),UPLOAD_PATH)
    REPORT_PATH='reports'
    REPORT_FOLDER=os.path.join(os.getcwd(),REPORT_PATH)
    SECRET_KEY = "test123"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False