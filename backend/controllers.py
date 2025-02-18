from flask import current_app as app
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import func

# ----- Protecting user to access admin dashboard and more ---------
def admin_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.role != 0:
            flash('You do not have permission to access this page.', 'danger')
            return redirect('/user') 
        return func(*args, **kwargs)
    return decorated_view

#--------------------- end ---------------------------------------

@app.route('/')
def home():
    return render_template('home.html', user=current_user)

# ------------------ Authentication --------------------------------------

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
            if not user:
                flash("User does not exist.", category='error')  
            elif check_password_hash(user.password, password):
                if user.role == 0:
                    flash("Logged in", category='success')
                    login_user(user, remember=True)
                    current_user.authenticated = True
                    return redirect('/admin')
                elif user.role == 1:
                    flash("Logged in", category='success')
                    login_user(user, remember=True)
                    current_user.authenticated = True
                    return redirect('/user')
            else:
                    flash("Password is incorrect.", category='error')
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
            user = User(email=email, password=generate_password_hash(password), name=name)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            current_user.authenticated = True
            flash("User created", category='success')
            return redirect('/user')
    return render_template("signup.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successfully", category='success')
    return redirect("/")


# --------------------- Admin Routes -------------------------------------

@app.route("/admin")
@login_required
def admin():
    subjects = Subject.query.order_by(Subject.id).all()
    chapters = Chapter.query.order_by(Chapter.id).all()
    return render_template("admin.html", user=current_user, subjects=subjects, chapters = chapters)

@app.route("/admin_quiz")
@login_required
def admin_quiz():
    quizzes = Quiz.query.order_by(Quiz.id).all()
    questions = Question.query.order_by(Question.id).all()
    return render_template('admin_quiz.html', user=current_user, quizzes=quizzes, questions=questions)

@app.route("/admin_summary")
@login_required
def admin_summary():
    return render_template('admin_summary.html', user=current_user)

@app.route("/new_subject", methods=['POST', 'GET'])
@login_required
def new_subject():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        subject = Subject(name=name, desc=desc)
        db.session.add(subject)
        db.session.commit()
        flash("Subject added", category='success')
        return redirect(url_for('admin'))
    return render_template("new_subject.html", user=current_user)

@app.route("/new_chapter/<int:subject_id>/", methods=['POST', 'GET'])
@login_required
# @admin_required
def new_chapter(subject_id):
    subject = Subject.query.filter_by(id =subject_id).first()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        chapter = Chapter(name=name, desc=desc, subject_id=subject.id)
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter added", category='success')
        return redirect(url_for('admin'))
    return render_template("new_chapter.html", user=current_user)

@app.route("/new_quiz", methods=['POST', 'GET'])
@login_required
# @admin_required
def new_quiz():
    chapters = Chapter.query.order_by(Chapter.id).all()
    if request.method == 'POST':
        date = request.form['date']
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        time = request.form['time']
        chap_id = int(request.form['selected_chapter'])
        quiz = Quiz(date=date_object, duration=time, chapter_id=chap_id)
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz added", category='success')
        return redirect(url_for('admin_quiz'))
    return render_template("new_quiz.html", user=current_user, chapters=chapters)

@app.route('/new_question/<int:quiz_id>/', methods=['GET', 'POST'])
def new_question(quiz_id):
    if request.method == 'POST':
        title = request.form['title']
        question_stmt = request.form['stmt']
        option_a = request.form['a']
        option_b = request.form['b']
        option_c = request.form['c']
        option_d = request.form['d']
        correct_option = request.form['correct_option']
        new_question = Question(
            title=title,
            question_stmt=question_stmt,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            quiz_id=quiz_id
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('admin_quiz'))
    return render_template('new_question.html',user=current_user, quiz_id=quiz_id)

#------- Editing the chapter From Admin and respective pages---------

@app.route('/chapter/<cid>/edit', methods=['GET', 'POST'])
def edit_chapter(cid):
    chapter = Chapter.query.get_or_404(cid)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.desc = request.form['desc']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_chapter.html', chapter=chapter)

#------- Deleting the chapter From Admin and respective pages---------

@app.route('/chapter/<cid>/delete', methods=["GET", "POST"])
def delete_chapter(cid):
    if request.method == "GET":
        try:
            chapter = Chapter.query.get_or_404(cid)
            for quiz in Quiz.query.filter_by(chapter_id=cid).all(): 
                Question.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz) 
            db.session.delete(chapter) 
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting chapter: {e}") 
            
# -------- Editing the questions from quiz ---------------------

@app.route('/question/<qid>/edit', methods=['GET', 'POST'])
def edit_question(qid):
    question = Question.query.get_or_404(qid)
    if request.method == 'POST':
        question.title = request.form['title']
        question.question_stmt = request.form['stmt']
        question.option_a = request.form['a']
        question.option_b = request.form['b']
        question.option_c = request.form['c']
        question.option_d = request.form['d']
        question.correct_option = request.form['correct_option']
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin_quiz', quiz_id=question.quiz_id))
    return render_template('edit_question.html', question=question)

# -------- Deleting the questions from quiz ---------------------

@app.route('/question/<qid>/delete', methods=['GET', 'POST'])
def delete_question(qid):
    if request.method == 'GET':
        try:
            question = Question.query.get_or_404(qid)
            db.session.delete(question)
            db.session.commit()
            return redirect(url_for('admin_quiz'))
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting question: {e}")

# -------------------- User Routes --------------------------------

@app.route("/user")
@login_required
def user():
    today = datetime.now().date()
    quizzes = Quiz.query.order_by(Quiz.date).all()
    return render_template("user.html", user=current_user, quizzes = quizzes)

@app.route('/user_scores')
@login_required
def user_scores():
    return render_template('user_scores.html', user=current_user)

@app.route("/user_summary")
@login_required
def user_summary():
    return render_template('user_summary.html', user=current_user)

@app.route("/quiz_view")
@login_required
def quiz_view():
    return render_template('quiz_view.html', user=current_user)

@app.route("/quiz_start")
@login_required
def quiz_start():
    return render_template('quiz_start.html', user=current_user)
