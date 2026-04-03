class Config:
    SECRET_KEY = "super-secret-key-123"

    # ✅ MAIL CONFIG
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'harshvardhansinghchouhan431@gmail.com'
    MAIL_PASSWORD = 'wpqnlxqiiodhywjf'
    MAIL_DEFAULT_SENDER = 'harshvardhansinghchouhan431@gmail.com'  

"""
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install flask flask_sqlalchemy flask_login flask_mail flask_migrate flask_limiter authlib gunicorn
pip freeze > requirements.txt
deactivate
"""