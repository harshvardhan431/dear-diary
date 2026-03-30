from datetime import date, datetime
from flask_login import UserMixin
from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

#flask db migrate -m "describe what changed"
# flask db upgrade

# rule:
# relationship()  -> class name
# ForeignKey()    -> table name
#always use back_populate over backref
# to update
#set FLASK_APP=main.py
#python -m flask db migrte -m "bages"
#python -m flask db upgrade
#python -m flask seed

 
class User(db.Model, UserMixin):
    __tablename__ = "users"

 #   id = db.Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    #uuid.uuid4 creates a unique id every time user is created UUID → a secure, globally unique identifier for your records, safer than integer IDs.
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), nullable=True,unique=True)    
    age = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False,index=True)#always add index for email 
    password = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
  #  city_id = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_diary_date = db.Column(db.Date)
    role=db.Column(db.String(20),default="user")
    profile = db.relationship("Profile", uselist=False, back_populates="user", cascade="all,delete-orphan")#back populates always point towards the object creating in parent side it links both side of data and makes them syncronized
    diaries = db.relationship("Diary", back_populates="user",cascade="all,delete-orphan", lazy=True) #uselist states that it returns only one values
    logins = db.relationship("LoginActivity", back_populates="user", lazy=True, cascade="all,delete-orphan")
    badge_links = db.relationship("UserBadge", back_populates="user", lazy=True, cascade="all,delete-orphan")

 #   city = db.relationship("City", back_populates="users")


# ================= PROFILE =================
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
  #  user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(200),default="default.png")

    user = db.relationship("User", back_populates="profile")


# ================= DIARY =================
class Diary(db.Model):
    __tablename__ = "diaries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id")) #where ever you find a foreign key put a index there 

    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at= db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    mood=db.Column(db.String(20))
    user = db.relationship("User", back_populates="diaries")


# ================= LOGIN ACTIVITY =================
class LoginActivity(db.Model):
    __tablename__ = "logins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    login_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    user = db.relationship("User", back_populates="logins")


# ================= STATE =================
class State(db.Model): #state is parnt to city
    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(100), nullable=True)

    city = db.relationship("City", back_populates="state", cascade="all,delete-orphan",lazy=True)


# ================= CITY =================
class City(db.Model): #city is  parent to user 
    __tablename__ = "city"

    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(100), nullable=True)
    state_id = db.Column(db.Integer, db.ForeignKey("states.id"))

    state = db.relationship("State", back_populates="city")
   # users = db.relationship("User", back_populates="city", cascade="all,delete-orphan")


# ================= BADGE =================
class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer , primary_key=True)
    bname = db.Column(db.String(100),nullable=True)
    description = db.Column(db.String(200))

    user_links = db.relationship("UserBadge", back_populates="badge",cascade="all,delete-orphan")


# ================= USER BADGE =================
class UserBadge(db.Model):
    __tablename__ = "user_badges"
    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"))

    user = db.relationship("User", back_populates="badge_links")
    badge = db.relationship("Badge", back_populates="user_links")
