from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)
    scores = db.relationship('Score', backref='user', lazy=True)

class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False, default="No Description")
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)
    
class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)
    
class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    question_stmt = db.Column(db.String(250), nullable=False)
    option_a = db.Column(db.String(250), nullable=False)
    option_b = db.Column(db.String(250), nullable=False)
    option_c = db.Column(db.String(250), nullable=False)
    option_d = db.Column(db.String(250), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # a, b, c, or d
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
class Score(db.Model):
    __tablename__ = "score"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)