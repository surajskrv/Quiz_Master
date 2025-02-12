from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    # qualification = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)

class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    chapters = db.relationship('AddChapter', backref='subject', lazy=True)

class AddChapter(db.Model):
    __tablename__ = "add_chapter"
    id = db.Column(db.Integer, primary_key=True)
    chapterName = db.Column(db.String(100), nullable=False)
    # qsn = db.Column(db.Integer, nullable=False, default=0)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
class New_Quiz(db.Model):
    __tablename__ = "new_quiz"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    question_title = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # a, b, c, or d
    chapter_id = db.Column(db.Integer, db.ForeignKey('add_chapter.id'), nullable=False)
    
    chapter = db.relationship('AddChapter', backref=db.backref('questions', lazy=True))