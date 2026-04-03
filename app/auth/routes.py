from flask import Blueprint,session
import secrets
from flask import render_template, request, jsonify, redirect, url_for,current_app
from werkzeug.security import generate_password_hash
from app.auth import bp #standard syntax of importing blueprint 
from app.utils import hash_password,verify_password,generate_email_token,verify_email_token,format_date 
from flask_mail import Message 
from app.extension import mail,oauth,limiter,cache
from app.forms import SignupForm,LoginupForm,DiaryForm
from app.models import State, City, User,Diary,Profile
from app.extension import db,login_manager
from flask_login import login_remembered,login_required,logout_user,login_user,current_user
from flask import flash
from datetime import date,timedelta
from werkzeug.utils import secure_filename
import uuid
import os
import logging
from datetime import datetime

@login_manager.user_loader #this decorator is used to restore the user data stored in database
def load_user(user_id):
    return User.query.get(int(user_id)) 


@bp.route("/")
def landing():
    return render_template("landing.html")

@bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def signup():
    form = SignupForm()

    print("SIGNUP ROUTE HIT")
    print("METHOD:", request.method)
    print("FORM DATA:", request.form)
    print("FORM ERRORS:", form.errors)

    if form.validate_on_submit():
        try:
            # 🔹 Check duplicate username
            existing_user = User.query.filter_by(username=form.name.data).first()
            if existing_user:
                flash("Username already exists. Try another.", "danger")
                return redirect(url_for("auth.signup"))

            # 🔹 Check duplicate email
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash("Email already registered.", "danger")
                return redirect(url_for("auth.signup"))

            # 🔹 Create user
            user = User(
                username=form.name.data.strip(),
                age=form.age.data,
                email=form.email.data,
                password=hash_password(form.password.data),
            )

            db.session.add(user)
            db.session.commit()
            print("✅ USER SAVED")

            # 🔹 Generate token & link
            token = generate_email_token(user.email)
            link = url_for("auth.verify_email", token=token, _external=True)

            # 🔹 Send email (separate try block)
            try:
                msg = Message(
                    subject="Verify your email",
                    sender=current_app.config['MAIL_USERNAME'],  # safer
                    recipients=[user.email],
                    body=f"Click to verify your email: {link}"
                )

                print("📧 SENDING MAIL...")
                mail.send(msg)
                print("✅ MAIL SENT")

            except Exception as mail_error:
                print("❌ MAIL ERROR:", mail_error)
                flash("Account created, but email not sent.", "warning")

            flash("Account created successfully! Please verify your email.", "success")
            return redirect(url_for("auth.email"))

        except Exception as e:
            db.session.rollback()
            print("🔥 FULL ERROR:", e)
            flash("Something went wrong. Please try again.", "danger")

    else:
        print("❌ FORM VALIDATION FAILED:", form.errors)

    return render_template("signup.html", form=form)
   #user signup and his details are stored in db then if the user click on the link then is_verified column is put to true .
   #if user account is delted or admin deletes it before user verifying then still he can't sign in 

@bp.route("/verify-email/<token>")
def verify_email(token):
    email = verify_email_token(token) #this line deocdes the email which was encode in the above code,checks expiry,signature

    if not email:
        return "Invalid or expired token"

    user = User.query.filter_by(email=email).first()
    user.is_verified = True
    db.session.commit()
    login_user(user) #here the user is autologin after clicking on the verification link,it set user is_authenticated=true
 #this tells flask that user is verified log him in and his id is stored in session so whenever @login_requiered is used we can retreicve that from session 
    return "Email verified"



@bp.route("/login/google")
def login_google():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google login is not configured yet.", "danger")
        return redirect(url_for("auth.login"))

    redirect_uri = url_for("auth.google_callback", _external=True)

    # Generate secure nonce
    nonce = secrets.token_urlsafe(16)

    # Store nonce in session
    session["google_nonce"] = nonce

    return oauth.google.authorize_redirect(
        redirect_uri,
        nonce=nonce
    )

@bp.route("/login/google/callback")
def google_callback():
    try:
        # Get token from Google
        token = oauth.google.authorize_access_token() 
    except Exception as e:
        current_app.logger.error(f"Google authorize_access_token failed: {e}")
        flash("Google authentication failed. Please try again.")
        return redirect(url_for("auth.login"))

    # Retrieve and remove nonce from session
    nonce = session.pop("google_nonce", None)

    if nonce is None:
        flash("Session expired. Please try again.")
        return redirect(url_for("auth.login"))

    try:
        # Verify ID token (signature, expiry, audience, nonce)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)
    except Exception as e:
        current_app.logger.error(f"ID token parsing failed: {e}")
        flash("Invalid authentication token.")
        return redirect(url_for("auth.login"))

    # Ensure email exists
    email = user_info.get("email")
    if not email:
        flash("Google account does not provide an email.")
        return redirect(url_for("auth.login"))

    # Ensure email is verified
    if not user_info.get("email_verified"):
        flash("Please verify your Google email before logging in.")
        return redirect(url_for("auth.login"))

    name = user_info.get("name", "Google User")

    # Check if user already exists
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=name,
            email=email,
            password=None, # Google users don't use passwords
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
    else:
        if not user.is_verified:
            user.is_verified = True
            db.session.commit()

    login_user(user)

    flash("Successfully logged in with Google.")
    return redirect(url_for("auth.home"))

@bp.route("/login/github") 
def login_github():
    if not current_app.config.get("GITHUB_CLIENT_ID") or not current_app.config.get("GITHUB_CLIENT_SECRET"):
        flash("GitHub login is not configured yet.", "danger")
        return redirect(url_for("auth.login"))

    redirect_uri = url_for("auth.github_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@bp.route("/login/github/callback")
def github_callback():
    token = oauth.github.authorize_access_token()

    # Get user info
    resp = oauth.github.get("user")
    user_info = resp.json()

    # GitHub email may not be in main response
    email_resp = oauth.github.get("user/emails")
    emails = email_resp.json()

    # Find primary email
    email = None
    for e in emails:
        if e.get("primary"):
            email = e.get("email")
            break

    if not email:
        flash("GitHub email not found")
        return redirect(url_for("auth.login"))
 
    name = user_info.get("login")

    # Same logic as Google
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=name,
            email=email,
            password=None,
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Logged in with GitHub")

    return redirect(url_for("auth.home"))

# ---------------- AJAX API ----------------
@bp.route("/get-cities/<int:state_id>")
def get_cities(state_id):
    cities = City.query.filter_by(state_id=state_id).all()

    data = [{"id": c.id, "name": c.name} for c in cities]
    return jsonify(data)

@bp.route("/login", methods=["POST", "GET"])
@limiter.limit("5 per minute")
def login():
    flash("login form is ","warning")
    logging.info("login route is accessed successfully")
    try:
        form = LoginupForm()

        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            user = User.query.filter_by(email=email).first()

            if user and user.password and verify_password(user.password, form.password.data):

                if not user.is_verified:
                    flash("Please verify your email before logging in.", "warning")
                    return redirect(url_for("auth.login"))

                # ✅ LOGIN ONLY IF PASSWORD IS CORRECT
                login_user(user, remember=form.remember.data)
                flash("Login successful", "success")
                return redirect(url_for("auth.home"))

            else:
                # ✅ THIS MUST BE INSIDE validate block
                flash("Invalid email or password", "danger")
                return redirect(url_for("auth.login"))

    except Exception as e:
        logging.error(f"login failed: {str(e)}")

    return render_template("login.html", form=form)

@bp.route("/diary",methods=["POST","GET"])
@login_required
def diary():
    dform=DiaryForm()
    today=date.today()

    if dform.validate_on_submit():
        if current_user.last_diary_date==today:
            flash("you have already submitted a diary today","warning")
            return redirect(url_for("auth.diary"))
        
        diary=Diary(
            title=dform.title.data,
            content=dform.content.data,
            mood=dform.mood.data,
            user_id=current_user.id
        )
        db.session.add(diary)
        yesterday=today-timedelta(days=1)

        if current_user.last_diary_date is None:
            current_user.streak=1
        elif current_user.last_diary_date==yesterday:
            current_user.streak+=1
        else:
            current_user.streak=0

        current_user.last_diary_date=today

        db.session.commit()
        return redirect(url_for("auth.home"))
       
    return render_template("diary.html",form=dform,current_date=today)

@bp.route("/monthly/<int:year>/<int:month>", methods=["POST","GET"])
@login_required
def monthly(year, month):
    diaries = Diary.query.filter(
        Diary.user_id == current_user.id,
        db.extract('year', Diary.created_at) == year,
        db.extract('month', Diary.created_at) == month
    ).order_by(Diary.created_at.desc()).all()

    return render_template("monthly_book.html", diaries=diaries, year=year, month=month)

@bp.route("/email",methods=["GET"])
def email():
    return render_template("check_email.html")
"""
@bp.route("/profile")
@login_required
def profile():
    current_app.logger.info("profile route is accessed")
    profile=current_user.profile

    if not profile:
        profile=Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()


    total_entry=Diary.query.filter_by(user_id=current_user.id).count()
    return render_template("profile.html",profile=profile,total_entry=total_entry)


@bp.before_app_request
def check_profile_completion():
    if current_user.is_authenticated:
        if current_user.age is None:
            if request.endpoint != "auth.complete_profile":
                return redirect(url_for("auth.complete_profile"))

@bp.route("/upload_profile_pic", methods=["POST"])
@login_required
def upload_profile_pic():

    file = request.files["profile_pic"] 

    if file:
        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)

        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        current_user.profile.profile_pic = filename
        db.session.commit()

    return redirect(url_for("auth.complete_profile"))"""

@bp.route("/home",methods=["POST","GET"])
@login_required
def home():
    current_app.logger.info("home route is accessed successfully")
    now=datetime.now()
    return render_template("home.html",year=now.year,month=now.month)

@bp.route("/about",methods=["GET"])
def about():
    return render_template("about.html")

@bp.route("/dashboard")
@cache.memoize(timeout=60)
def dashboard():
    current_app.logger.info("dashboard route is successfully accessed")
    total_entries=Diary.query.filter_by(user_id=current_user.id).count()
    recent_entries=Diary.query.filter_by(user_id=current_user.id).order_by(Diary.date.desc()).limit(100).all()

    return render_template("dashboard.html",total_entries=total_entries,recent_entries=recent_entries)




