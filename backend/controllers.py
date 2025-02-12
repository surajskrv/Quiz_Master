from flask import render_template, redirect,request
from backend.models import *
from flask import current_app as app
from flask import flash
from wtforms import Form, StringField, PasswordField, validators
import re

def is_valid_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email:
            flash("Email is required.", category='error')
        elif not is_valid_email(email):
            flash("Invalid email format.", category='error')
        elif not password:
            flash("Password is required.", category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                if user.password == password:
                    flash("Logged in", category='success')
                    return redirect('/')
                else:
                    flash("Password is incorrect.", category='error')
            else:
                flash("User does not exist.", category='error')
                
    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        name = request.form['name']
        
        if not email:
            flash("Email is required.", category='error')
        elif not is_valid_email(email):
            flash("Invalid email format.", category='error')
        elif len(name) <=2:
            flash("Name is too short.", category='error')
        elif len(password) <= 6:
            flash("Password must at least 6 characters", category='error')
        elif password != password2:
            flash("Passwords do not match.", category='error')
        elif User.query.filter_by(email=email).first():
            flash("User already exists.", category='error')
        else:
            flash("User created", category='success')
            user = User(email=email, password=password, name=name)
            db.session.add(user)
            db.session.commit()
    
    return render_template("signup.html")

@app.route("/logout", methods=['POST', 'GET'])
def logout():
    return redirect('/')

@app.route("/about")
def about():
    return render_template("about.html")