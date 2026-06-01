import uuid
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

pages_bp = Blueprint("pages", __name__)


def get():
    from app import db, User, LearningSession, Achievement, QuizResult, StudyPlan, Note
    return db, User, LearningSession, Achievement, QuizResult, StudyPlan, Note


@pages_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))
    return render_template("landing.html")


@pages_bp.route("/dashboard")
@login_required
def dashboard():
    _, _, LS, Ach, QR, SP, _ = get()
    return render_template("pages/dashboard.html", user=current_user,
        recent_sessions = LS.query.filter_by(user_id=current_user.id).order_by(LS.started_at.desc()).limit(5).all(),
        recent_ach      = Ach.query.filter_by(user_id=current_user.id).order_by(Ach.earned_at.desc()).limit(6).all(),
        recent_quiz     = QR.query.filter_by(user_id=current_user.id).order_by(QR.taken_at.desc()).limit(5).all(),
        active_plans    = SP.query.filter_by(user_id=current_user.id, is_active=True).all(),
        total_ach       = Ach.query.filter_by(user_id=current_user.id).count())


@pages_bp.route("/tutor")
@login_required
def tutor():
    db, _, LS, *_ = get()
    session_id = str(uuid.uuid4())
    subject    = request.args.get("subject", "General")
    topic      = request.args.get("topic", "Open Learning")
    s = LS(session_id=session_id, user_id=current_user.id, subject=subject, topic=topic)
    db.session.add(s); db.session.commit()
    return render_template("pages/tutor.html", user=current_user,
                           session_id=session_id, subject=subject, topic=topic)


@pages_bp.route("/quiz")
@login_required
def quiz():
    return render_template("pages/quiz.html", user=current_user)


@pages_bp.route("/study-plans")
@login_required
def study_plans():
    _, _, _, _, _, SP, _ = get()
    plans = SP.query.filter_by(user_id=current_user.id).order_by(SP.created_at.desc()).all()
    return render_template("pages/study_plans.html", user=current_user, plans=plans)


@pages_bp.route("/analytics")
@login_required
def analytics():
    return render_template("pages/analytics.html", user=current_user)


@pages_bp.route("/notes")
@login_required
def notes():
    _, _, _, _, _, _, Note = get()
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(
        Note.is_pinned.desc(), Note.created_at.desc()).all()
    return render_template("pages/notes.html", user=current_user, notes=user_notes)


@pages_bp.route("/leaderboard")
@login_required
def leaderboard():
    _, User, *_ = get()
    top_users = User.query.order_by(User.xp_points.desc()).limit(20).all()
    user_rank = User.query.filter(User.xp_points > current_user.xp_points).count() + 1
    return render_template("pages/leaderboard.html", user=current_user,
                           top_users=top_users, user_rank=user_rank)


@pages_bp.route("/profile")
@login_required
def profile():
    _, _, _, Ach, QR, *_ = get()
    recent_quiz  = QR.query.filter_by(user_id=current_user.id).order_by(QR.taken_at.desc()).limit(10).all()
    avg_score    = round(sum(q.score for q in recent_quiz) / max(len(recent_quiz), 1), 1)
    achievements = Ach.query.filter_by(user_id=current_user.id).order_by(Ach.earned_at.desc()).all()
    return render_template("pages/profile.html", user=current_user,
                           achievements=achievements, recent_quiz=recent_quiz, avg_score=avg_score)
