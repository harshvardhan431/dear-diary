import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    # ✅ MAIL CONFIG
    MAIL_SERVER = os.getenv('MATL_SERVER')
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID= os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET=os.getenv('GITHUB_CLIENT_SECRET')
"""
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install flask flask_sqlalchemy flask_login flask_mail flask_migrate flask_limiter authlib gunicorn
pip freeze > requirements.txt
deactivate
"""