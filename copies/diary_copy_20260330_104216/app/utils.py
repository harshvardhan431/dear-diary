from werkzeug.security import check_password_hash,generate_password_hash
from flask import current_app #helps use to access secret key tokens app config
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired

def hash_password(password: str) ->str: #-> str means that it will return a string 
    return generate_password_hash(password)

def verify_password(hashed_password:str ,password:str)->bool:
    return check_password_hash(hashed_password,password)

def generate_email_token(email:str)->str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])#Uses SECRET_KEY to cryptographically sign the token
    return serializer.dumps(email, salt="email-verify")
#takes a email adds some salt to it creats a signed +tamper proof token and returns it
#this creates a secure token for email verification and token expires after one hour 

def verify_email_token(token:str,max_age:int =3600)->str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email=serializer.loads(token, salt="email-verify", max_age=max_age) #load is used for deserialization of token it remove the salt and gets teh orginal email
        return email #the above line checks the verify the signature
    except SignatureExpired: #token expired
        return None
    except BadSignature: #token is tampered,,signature is secret stamp that proves the token ws created by your server  and data is not verified
        return None 
#verify the email from link returns email if valid otherwise raises an exception 

def format_date(date_obj) ->str:
    return date_obj.strftime("%Y-%m-%d %H:%M") #this is used to return a date in form of string 