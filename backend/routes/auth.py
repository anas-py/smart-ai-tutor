import json, datetime
from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)


def get():
    # Import inside function — runs AFTER app.py fully loads, no circular issue
    from app import db, User, Achievement
    return db, User, Achievement


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))
    if request.method == "POST":
        db, User, Achievement = get()
        data     = request.get_json(silent=True) or request.form
        email    = (data.get("email") or "").strip().lower()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if not email or not username or not password:
            return jsonify({"error": "All fields are required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        subjects = data.get("subjects", [])
        if isinstance(subjects, str):
            try:    subjects = json.loads(subjects)
            except: subjects = []
        user = User(
            username=username, email=email,
            full_name=(data.get("full_name") or "").strip(),
            grade_level=data.get("grade_level", "High School"),
            learning_style=data.get("learning_style", "visual"),
            avatar=data.get("avatar", "🎓"),
            subjects=json.dumps(subjects),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        ach = Achievement(user_id=user.id, key="welcome", title="Welcome Scholar!",
                          description="Joined NeuroTutor AI", icon="🌟",
                          category="milestone", xp_value=100)
        db.session.add(ach)
        user.add_xp(100)
        db.session.commit()
        login_user(user)
        token = create_access_token(identity=user.id)
        return jsonify({"success": True, "token": token, "redirect": url_for("pages.dashboard")})
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))
    if request.method == "POST":
        db, User, _ = get()
        data     = request.get_json(silent=True) or request.form
        email    = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        remember = bool(data.get("remember", False))
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        login_user(user, remember=remember)
        user.last_active    = datetime.datetime.utcnow()
        user.total_sessions += 1
        db.session.commit()
        token = create_access_token(identity=user.id)
        return jsonify({"success": True, "token": token, "redirect": url_for("pages.dashboard")})
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
