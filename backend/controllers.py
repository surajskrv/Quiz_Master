from flask import current_app as app
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import func, distinct
from collections import defaultdict

@app.route('/')
def home():
    return render_template('home.html', user=current_user)

# ------------------ Authentication --------------------------------------

# ------------- login ------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
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
    except:
        return redirect('/login')
    return render_template('login.html', user=current_user)

# ----------------- Signup -------------------
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

# ----------------- Logout -----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successfully", category='success')
    return redirect("/")

# --------------------- Admin Routes -------------------------------------

# Admin dashboard
@app.route("/admin")
@login_required
def admin():
    subjects = Subject.query.order_by(Subject.id).all()
    chapters = Chapter.query.order_by(Chapter.id).all()
    for chapter in chapters:
        no_of_questions = sum(len(quiz.questions) for quiz in chapter.quizzes)
        setattr(chapter, 'no_of_questions', no_of_questions)
    return render_template("admin.html", user=current_user, subjects=subjects, chapters = chapters)

# Admin Quiz Page
@app.route("/admin_quiz")
@login_required
def admin_quiz():
    quizzes = Quiz.query.order_by(Quiz.id).all()
    questions = Question.query.order_by(Question.id).all()
    return render_template('admin_quiz.html', user=current_user, quizzes=quizzes, questions=questions)

# Admin Summary Page
@app.route("/admin_summary")
@login_required
def admin_summary():
    max_scores = db.session.query(Subject.name, func.max(Score.score).label('max_score')).\
        join(Chapter, Subject.id == Chapter.subject_id).\
        join(Quiz, Chapter.id == Quiz.chapter_id).\
        join(Score, Quiz.id == Score.quiz_id).\
        group_by(Subject.name).all()

    subject_users = defaultdict(list)
    for subject, max_score in max_scores:
        users = db.session.query(User.name).\
            join(Score, User.id == Score.user_id).\
            join(Quiz, Score.quiz_id == Quiz.id).\
            join(Chapter, Quiz.chapter_id == Chapter.id).\
            join(Subject, Chapter.subject_id == Subject.id).\
            filter(Subject.name == subject, Score.score == max_score).all()
        subject_users[subject] = [user[0] for user in users]

    subject_attempts = db.session.query(Subject.name, func.count(Score.id).label('attempts')).\
        join(Chapter, Subject.id == Chapter.subject_id).\
        join(Quiz, Chapter.id == Quiz.chapter_id).\
        join(Score, Quiz.id == Score.quiz_id).\
        group_by(Subject.name).all()

    subject_labels = [subject for subject, _ in max_scores]
    top_scores = [max_score for _, max_score in max_scores]
    attempts = [attempts for _, attempts in subject_attempts]

    return render_template('admin_summary.html', user=current_user, subject_users=subject_users, max_scores=max_scores, subject_labels=subject_labels, top_scores=top_scores, attempts=attempts)

# Admin Search Page
@app.route("/admin/search", methods=['GET'])
@login_required
def admin_search():
    query = request.args.get('query')
    search_type = request.args.get('search_type')

    results = []

    if query:
        if search_type == 'users':
            results = User.query.filter(User.email.ilike(f"%{query}%")).all()
        elif search_type == 'subjects':
            results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        elif search_type == 'quizzes':
            results = Quiz.query.join(Chapter).filter(Chapter.name.ilike(f"%{query}%")).all()
        else:
            flash("Please select a search type.", category='error')
            return redirect(url_for('admin'))

    return render_template('admin_search.html', user=current_user, results=results, query=query, search_type=search_type)

# Admin New Subject Page
@app.route("/new_subject", methods=['POST', 'GET'])
@login_required
def new_subject():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        if name and desc:
            existing_subject = Subject.query.filter_by(name = name).first()
            if not existing_subject:
                new_subject = Subject(name=name, desc=desc)
                db.session.add(new_subject)
                db.session.commit()
                flash("Subject added", category='success')
                return redirect(url_for('admin'))
            else:
                flash("Subject already exists", category='error')
        else:
            flash("Both fields are required", category='error')
    return render_template("new_subject.html", user=current_user)

# Admin New Chapter Page
@app.route("/new_chapter/<int:subject_id>/", methods=['POST', 'GET'])
@login_required
def new_chapter(subject_id):
    subject = Subject.query.filter_by(id =subject_id).first()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        if name and desc:
            existing_chapter = Chapter.query.filter_by(name = name).first()
            if not existing_chapter:
                new_chapter = Chapter(name=name, desc=desc, subject_id=subject.id)
                db.session.add(new_chapter)
                db.session.commit()
                flash("Chapter added", category='success')
                return redirect(url_for('admin'))
            else:
                flash("Chapter already exists", category='error')
        else:
            flash("Both fields are required", category='error')
    return render_template("new_chapter.html", user=current_user)

# Admin New Quiz Page
@app.route("/new_quiz", methods=['POST', 'GET'])
@login_required
def new_quiz():
    chapters = Chapter.query.order_by(Chapter.id).all()
    if request.method == 'POST':
        date = request.form['date']
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        time = request.form['time']
        chap_id = int(request.form.get('selected_chapter'))
        if not chap_id or chap_id not in [chapter.id for chapter in chapters]:
            flash("Invalid Chapter", category='error')
            return redirect(url_for('admin_quiz'))
        if date and time and chap_id:
            existing_quiz = Quiz.query.filter_by(date = date_object, chapter_id = chap_id).first()
            if existing_quiz:
                flash("Quiz already exists", category='error')
                return redirect(url_for('admin_quiz'))
            else:
                new_quiz = Quiz(date=date_object, duration=time, chapter_id=chap_id)
                db.session.add(new_quiz)
                db.session.commit()
                flash("Quiz added", category='success')
                return redirect(url_for('admin_quiz'))
        else:
            flash("All fields are required", category='error')
    return render_template("new_quiz.html", user=current_user, chapters=chapters)

# Admin New Question Page
@app.route('/new_question/<int:quiz_id>/', methods=['GET', 'POST'])
@login_required
def new_question(quiz_id):
    if request.method == 'POST':
        title = request.form['title']
        question_stmt = request.form['stmt']
        option_a = request.form['a']
        option_b = request.form['b']
        option_c = request.form['c']
        option_d = request.form['d']
        correct_option = request.form.get('correct_option')        
        if not correct_option or correct_option not in ['a', 'b', 'c', 'd']:
            flash("Invalid correct option", category='error')
            return redirect(url_for('admin_quiz'))
        else:
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

#------- Editing in Admin and respective pages---------

@app.route('/subject/<sid>/edit', methods=['GET', 'POST'])
@login_required
def edit_subject(sid):
    subject = Subject.query.get_or_404(sid)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.desc = request.form['desc']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_subject.html', subject=subject)

@app.route('/chapter/<cid>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(cid):
    chapter = Chapter.query.get_or_404(cid)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.desc = request.form['desc']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/quiz/<qid>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(qid):
    quiz = Quiz.query.get_or_404(qid)
    chapters = Chapter.query.order_by(Chapter.id).all()
    if request.method == 'POST':
        date = request.form['date']
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        quiz.date = date_object
        quiz.duration = request.form['time']
        quiz.chapter_id = int(request.form.get('selected_chapter'))
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin_quiz'))
    return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

@app.route('/question/<qid>/edit', methods=['GET', 'POST'])
@login_required
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

#------- Deleting in Admin and respective pages---------

@app.route('/subject/<sid>/delete', methods=["GET", "POST"])
@login_required
def delete_subject(sid):    
    if request.method == "GET":
        try:
            subject = Subject.query.get_or_404(sid)
            for chapter in Chapter.query.filter_by(subject_id=sid).all():
                for quiz in Quiz.query.filter_by(chapter_id=chapter.id).all():
                    Score.query.filter_by(quiz_id=quiz.id).delete()
                    Question.query.filter_by(quiz_id=quiz.id).delete()
                    db.session.delete(quiz)
                db.session.delete(chapter)
            db.session.delete(subject)
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting subject: {e}")

@app.route('/chapter/<cid>/delete', methods=["GET", "POST"])
@login_required
def delete_chapter(cid):
    if request.method == "GET":
        try:
            chapter = Chapter.query.get_or_404(cid)
            for quiz in Quiz.query.filter_by(chapter_id=cid).all(): 
                Score.query.filter_by(quiz_id=quiz.id).delete()
                Question.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz) 
            db.session.delete(chapter) 
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting chapter: {e}") 
            
@app.route('/quiz/<qid>/delete', methods=["GET", "POST"])
@login_required
def delete_quiz(qid):
    if request.method == "GET":
        try:
            quiz = Quiz.query.get_or_404(qid)
            Score.query.filter_by(quiz_id=quiz.id).delete()
            Question.query.filter_by(quiz_id=qid).delete()
            db.session.delete(quiz)
            db.session.commit()
            flash("Quiz deleted successfully!", "success")
            return redirect(url_for('admin_quiz'))
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting quiz: {e}")

@app.route('/question/<qid>/delete', methods=['GET', 'POST'])
@login_required
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
            
# --------------- end ----------------

# -------------------- User Routes --------------------------------

# User Dashboard
@app.route("/user")
@login_required
def user():
    quizzes = Quiz.query.order_by(Quiz.date).all()
    return render_template("user.html", user=current_user, quizzes = quizzes)

# User Scores Page
@app.route('/user_scores')
@login_required
def user_scores():
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    score_data = []
    for score_entry in user_scores:
        quiz = Quiz.query.get(score_entry.quiz_id)
        if quiz:
            chapter = Chapter.query.get(quiz.chapter_id)
            if chapter:
                score_data.append({
                    'quiz_date': score_entry.date,
                    'chapter_name': chapter.name,
                    'score': score_entry.score,
                    'total_questions': len(quiz.questions)
                })
    return render_template('user_scores.html', user=current_user, scores=score_data)

# User Summary Page
@app.route("/user_summary")
@login_required
def user_summary():
    subject_summary = db.session.query(Subject.name, func.count(Score.id)).\
        join(Chapter, Subject.id == Chapter.subject_id).\
        join(Quiz, Chapter.id == Quiz.chapter_id).\
        join(Score, Quiz.id == Score.quiz_id).\
        filter(Score.user_id == current_user.id).\
        group_by(Subject.name).all()

    month_summary = db.session.query(func.strftime('%Y-%m', Score.date), func.count(Score.id)).\
        filter(Score.user_id == current_user.id).\
        group_by(func.strftime('%Y-%m', Score.date)).all()

    subject_labels = [subject for subject, _ in subject_summary]
    subject_data = [count for _, count in subject_summary]

    month_labels = [month for month, _ in month_summary]
    month_data = [count for _, count in month_summary]

    return render_template('user_summary.html', user=current_user, subject_labels=subject_labels, subject_data=subject_data, month_labels=month_labels, month_data=month_data)

# Quiz view page for user
@app.route("/quiz_view/<int:qid>/")
@login_required
def quiz_view(qid):
    quiz = Quiz.query.get_or_404(qid)
    chapter = quiz.chapter
    subject = chapter.subject
    return render_template('quiz_view.html', user=current_user, quiz=quiz, chapter=chapter, subject=subject)

# quiz start page for user
@app.route("/quiz_start/<int:qid>/")
@login_required
def quiz_start(qid):
    quiz = Quiz.query.get_or_404(qid)
    questions = quiz.questions
    duration_str = quiz.duration
    try:
        time = duration_str.split(':')
        hours = int(time[0])
        minutes = int(time[1])
        total_seconds = hours * 3600 + minutes * 60
    except ValueError:
        total_seconds = 0

    return render_template('quiz_start.html', user=current_user, quiz=quiz, questions=questions,duration_seconds=total_seconds)

# quiz submission page for user
@app.route("/submit_quiz/<int:qid>", methods=['POST'])
@login_required
def submit_quiz(qid):
    quiz = Quiz.query.get_or_404(qid)
    questions = quiz.questions
    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer == question.correct_option:
            score += 1
    today = datetime.now().date()
    existing_score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
    if existing_score:
        existing_score.score = score
        existing_score.date = today.strftime('%Y-%m-%d')
    else:
        new_score = Score(user_id=current_user.id, quiz_id=quiz.id, score=score, date=today.strftime('%Y-%m-%d'))
        db.session.add(new_score)
    db.session.commit()
    return redirect(url_for('quiz_result', qid=quiz.id, score=score))

# Quiz result page
@app.route("/quiz_result/<int:qid>/<int:score>")
@login_required
def quiz_result(qid, score):
    quiz = Quiz.query.get_or_404(qid)
    total_questions = len(quiz.questions)
    return render_template('quiz_result.html', user=current_user, quiz=quiz, score=score, total_questions=total_questions)