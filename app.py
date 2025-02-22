from flask import Flask
from backend.models import *
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = None

def create_admin():
    admin = User.query.filter_by(role=0).first()
    if not admin:
        admin = User(email="admin@gmail.com", password=generate_password_hash("hello@123"), name="admin", role=0)
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully.")
    else:
        print("Admin already exists.")
        

def start():
    quiz_app = Flask(__name__)
    quiz_app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_db.sqlite3"
    quiz_app.config["SECRET_KEY"] = "this_is_a_secret_for_quiz_app"
    db.init_app(quiz_app)
    quiz_app.app_context().push()
    quiz_app.debug = True
    db.create_all()
    # adding admin to db
    create_admin()
    
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(quiz_app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    print("Quiz app is running... ")
    
app = start()

from backend.controllers import *

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
