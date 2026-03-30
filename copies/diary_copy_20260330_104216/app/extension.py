from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth 
from flask_caching import Cache
from flask_mail import Mail
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view="auth.login" #this auth is the blueprint name taken for endpoint
oauth = OAuth()
csrf=CSRFProtect() #the csrf tojen is saved in server session
cache=Cache() #it has a timelimit as data may change it for data that does not change frequently
mail=Mail()
migrate=Migrate() #helps you add column ,delete column ,makes changes in db
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


logging.info("extension failed")