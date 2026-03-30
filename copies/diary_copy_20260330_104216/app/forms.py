from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,IntegerField,EmailField,PasswordField,SubmitField,IntegerRangeField,BooleanField,TextAreaField,RadioField
from wtforms.validators import DataRequired,Length,ValidationError,Email,EqualTo,NumberRange
from app.models import User
class SignupForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired(message="name is compulsory"),Length(min=5,message="name must be five characters")],render_kw={"placeholder":"enter your name "})
    age=IntegerRangeField("Age",validators=[DataRequired(),NumberRange(min=5,max=80)],render_kw={"min":5,"max":80,"step":1})
    email=EmailField("Email",validators=[DataRequired(),Email()],render_kw={"placeholder":"enter your email"})
    password=PasswordField("Password",validators=[DataRequired()],render_kw={"placeholder":"enter a secure password"})
    recheck_password=PasswordField("Password",validators=[DataRequired(),EqualTo('password',message="password must be same")],render_kw={"placeholder":"enter the same passoword"})
    submit = SubmitField("Sign Up")
    def validate_email(self, email):#without this self the python crashes ,python always passes the object as argument, **self is form and email means email field
     if User.query.filter_by(email=email.data).first(): #here email.data is the email given by user 
         raise ValidationError("Email already registered")
     
class LoginupForm(FlaskForm):
   email=EmailField("Email",validators=[DataRequired(),Email()],render_kw={"placeholder":"enter your email"})
   password=PasswordField("Password",validators=[DataRequired()],render_kw={"placeholder":"enter a secure password"})
   remember=BooleanField("remember me")
   submit = SubmitField("Submit") 

class DiaryForm(FlaskForm):
   title=StringField("title",validators=[DataRequired(message="title is compulsory")],render_kw={"placeholder":"enter the title"})
   content=TextAreaField("dear diary ",validators=[DataRequired(message="it is compulsory to write diary"),Length(max=600,message="you can write upto 600 words")])
   mood=RadioField("how are you feeling?",choices=[("happy", "😊"),("normal", "😐"),("sad", "😢"),("angry", "😡")])
   submit=SubmitField("submit")  