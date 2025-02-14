from flask import current_app as app
from flask import render_template, redirect, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import *
from werkzeug.security import check_password_hash, generate_password_hash

@login_required
@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("user.html", user=current_user)
    else:
        return redirect("/login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email:
            flash("Email is required.", category='error')
        elif not password:
            flash("Password is required.", category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user.email == 'admin@gmail.com':
                return redirect('/admin')
            elif user:
                if check_password_hash(user.password, password):
                    flash("Logged in", category='success')
                    login_user(user, remember=True)
                    current_user.authenticated = True
                    return redirect('/')
                else:
                    flash("Password is incorrect.", category='error')
            else:
                flash("User does not exist.", category='error')  
    return render_template('login.html', user=current_user)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        name = request.form['name']
        
        if not email:
            flash("Email is required.", category='error')
        elif len(name) <=2:
            flash("Name is too short.", category='error')
        elif len(password) <= 6:
            flash("Password must at least 6 characters", category='error')
        elif password != password2:
            flash("Passwords do not match.", category='error')
        elif User.query.filter_by(email=email).first():
            flash("User already exists.", category='error')
        else:
            user = User(email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), name=name)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            current_user.authenticated = True
            flash("User created", category='success')
            return redirect('/')
    return render_template("signup.html", user=current_user)

@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash("Logout Successfully", category='success')
    return redirect("/")

@app.route("/admin")
def admin():
    return render_template("admin.html", user=current_user)