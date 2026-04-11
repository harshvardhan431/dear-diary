import os
from pathlib import Path

from dotenv import load_dotenv #reades varible from .env file and puts them to environment folder 
from flask import Flask, flash, redirect, url_for

from app.extension import cache, csrf, db, limiter, login_manager, mail, migrate, oauth
from app.auth import bp
from app.commands import register_commands
from app.config_log import setup_logger
from config import Config
from app import models  # noqa: F401


ROOT_DIR = Path(__file__).resolve().parent.parent # this gives the root folder of project
load_dotenv(ROOT_DIR / ".env", override=True) #loads the environment variable from your env file
#here override =true means if variable already exist replace it with this one if secret key or any other varibale are chagnes then this lines help to override it 

def create_app(): #this is application factory where app is created inside the function
    app = Flask(__name__)
    setup_logger(app)
    app.config.from_object(Config)
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = "redis://localhost:6379/0"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300

    for key in (
        "SECRET_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GITHUB_CLIENT_ID",
        "GITHUB_CLIENT_SECRET",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_DEFAULT_SENDER",
    ):
        value = os.getenv(key)
        if value:
            app.config[key] = value

    if app.config.get("MAIL_USERNAME") and not app.config.get("MAIL_DEFAULT_SENDER"):
        app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "profile_pics")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{ROOT_DIR / 'instance' / 'data.db'}"
    """
    sqlite:///relative/path.db
sqlite:////absolute/path.db
    """
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    try:
        cache.init_app(app)
        app.logger.info("cache initialzed successfully with redis")
    except Exception as exc:
        app.logger.warning(f"app cannot work with redis use simplecache {exc}")
        app.config["CACHE_TYPE"] = "SimpleCache"
        cache.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    oauth.init_app(app)
    register_commands(app)
    app.logger.info("extension initiallized successfully")

    def rate_limit_exceeded(_error):
        flash("Too many requests. Please try again later.", "danger")
        return redirect(url_for("auth.login"))

    app.register_error_handler(429, rate_limit_exceeded)
    app.register_blueprint(bp, url_prefix="")

    oauth.register(
        name="google",
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    oauth.register(
        name="github",
        client_id=app.config.get("GITHUB_CLIENT_ID"),
        client_secret=app.config.get("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

    if not app.config.get("SECRET_KEY"):
        raise ValueError("SECRET_KEY is missing!")

    app.logger.info("App configuration loaded successfully")
    return app
