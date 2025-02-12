from flask import Flask, render_template
from backend.models import *

app = None

def start():
    quiz_app = Flask(__name__)
    quiz_app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_db.sqlite3"
    quiz_app.config["SECRET_KEY"] = "thisisasecretforquizapp"
    db.init_app(quiz_app)
    quiz_app.app_context().push()
    quiz_app.debug = True
    db.create_all()
    print("Quiz app is running... ")
    
app = start()

from backend.controllers import *

if __name__ == "__main__":
    app.run()