import json, datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

api_bp  = Blueprint("api", __name__)
_agents = {}


def get():
    from app import db, User, LearningSession, Achievement, QuizResult, StudyPlan, Note
    return db, User, LearningSession, Achievement, QuizResult, StudyPlan, Note


def agent(name):
    if name not in _agents:
        if name == "tutor":
            from backend.agents.tutor_agent import TutorAgent
            _agents[name] = TutorAgent()
        elif name == "quiz":
            from backend.agents.quiz_agent import QuizAgent
            _agents[name] = QuizAgent()
        elif name == "plan":
            from backend.agents.study_plan_agent import StudyPlanAgent
            _agents[name] = StudyPlanAgent()
        elif name == "analytics":
            from backend.agents.analytics_agent import AnalyticsAgent
            _agents[name] = AnalyticsAgent()
    return _agents[name]


def ach_engine():
    if "ach" not in _agents:
        from app import db, User, Achievement
        from backend.agents.analytics_agent import AchievementEngine
        _agents["ach"] = AchievementEngine(db, User, Achievement)
    return _agents["ach"]


@api_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    db, _, LS, *_ = get()
    data       = request.get_json(force=True)
    message    = (data.get("message") or "").strip()
    session_id = data.get("session_id")
    mode       = data.get("mode", "tutor")
    subject    = data.get("subject", "General")
    if not message:
        return jsonify({"error": "Empty message"}), 400
    ls      = LS.query.filter_by(session_id=session_id, user_id=current_user.id).first()
    history = ls.get_messages() if ls else []
    result  = agent("tutor").chat(message=message, history=history, mode=mode, subject=subject,
                user_context={"name": current_user.display_name, "grade_level": current_user.grade_level,
                              "learning_style": current_user.learning_style,
                              "subjects": current_user.get_subjects(), "level": current_user.level})
    history.append({"role":"user","content":message,"timestamp":datetime.datetime.utcnow().isoformat()})
    history.append({"role":"assistant","content":result["content"],"timestamp":datetime.datetime.utcnow().isoformat(),"mode":mode})
    if ls:
        ls.messages = json.dumps(history); ls.agent_mode = mode
        ls.msg_count = len([m for m in history if m["role"]=="user"]); ls.xp_earned += 10
    current_user.total_questions += 1
    leveled_up = current_user.add_xp(10)
    db.session.commit()
    new_ach = ach_engine().check_and_award(current_user.id, "question", {"level": current_user.level})
    return jsonify({"response": result["content"], "agent_steps": result.get("agent_steps",[]),
                    "resources": result.get("resources",[]), "follow_up_questions": result.get("follow_up_questions",[]),
                    "xp_earned": 10, "total_xp": current_user.xp_points, "level": current_user.level,
                    "new_achievements": new_ach, "leveled_up": leveled_up})


@api_bp.route("/quiz/generate", methods=["POST"])
@login_required
def generate_quiz():
    data = request.get_json(force=True)
    return jsonify(agent("quiz").generate_quiz(
        subject=data.get("subject","Mathematics"), topic=data.get("topic",""),
        difficulty=data.get("difficulty","medium"), num_questions=int(data.get("num_questions",5)),
        user_level=current_user.level))


@api_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz():
    db, _, _, _, QR, *_ = get()
    data   = request.get_json(force=True)
    result = agent("quiz").evaluate_quiz(data.get("answers",{}), data.get("quiz_data",{}))
    xp     = max(5, int(result["score"] * 2))
    qr = QR(user_id=current_user.id, subject=data.get("subject","General"),
            topic=data.get("topic",""), difficulty=data.get("quiz_data",{}).get("difficulty","medium"),
            score=result["score"], total_questions=result["total"], correct_answers=result["correct"],
            time_taken_secs=data.get("time_taken",0), grade=result["grade"],
            quiz_data=json.dumps({"feedback": result["feedback"]}))
    db.session.add(qr)
    current_user.total_quiz_taken += 1
    current_user.add_xp(xp)
    db.session.commit()
    new_ach = ach_engine().check_and_award(current_user.id, "quiz_complete", {"score": result["score"]})
    return jsonify({**result, "xp_earned": xp, "total_xp": current_user.xp_points, "new_achievements": new_ach})


@api_bp.route("/study-plan/generate", methods=["POST"])
@login_required
def generate_study_plan():
    db, _, _, _, _, SP, _ = get()
    data = request.get_json(force=True)
    plan = agent("plan").generate_plan(
        subject=data.get("subject","Mathematics"), goal=data.get("goal",""),
        deadline=data.get("deadline",""), hours_per_day=float(data.get("hours_per_day",2)),
        current_level=data.get("current_level","beginner"),
        user_context={"grade": current_user.grade_level, "style": current_user.learning_style})
    deadline_dt = None
    if data.get("deadline"):
        try: deadline_dt = datetime.datetime.fromisoformat(data["deadline"])
        except: pass
    sp = SP(user_id=current_user.id, title=plan.get("title","Plan"), subject=data.get("subject"),
            goal=data.get("goal",""), plan_data=json.dumps(plan), deadline=deadline_dt)
    db.session.add(sp); db.session.commit()
    plan["plan_id"] = sp.id
    return jsonify(plan)


@api_bp.route("/study-plan/<int:plan_id>", methods=["GET","DELETE"])
@login_required
def study_plan(plan_id):
    db, _, _, _, _, SP, _ = get()
    sp = SP.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    if request.method == "DELETE":
        db.session.delete(sp); db.session.commit(); return jsonify({"success": True})
    pd = json.loads(sp.plan_data or "{}")
    return jsonify({**pd, "plan_id": sp.id, "title": sp.title, "subject": sp.subject, "progress": sp.progress})


@api_bp.route("/analytics")
@login_required
def analytics_data():
    _, _, LS, Ach, QR, *_ = get()
    return jsonify(agent("analytics").get_user_analytics(
        user_id=current_user.id,
        sessions=LS.query.filter_by(user_id=current_user.id).all(),
        quiz_results=QR.query.filter_by(user_id=current_user.id).all(),
        achievements=Ach.query.filter_by(user_id=current_user.id).all()))


@api_bp.route("/notes", methods=["GET","POST"])
@login_required
def notes():
    db, _, _, _, _, _, Note = get()
    if request.method == "POST":
        data = request.get_json(force=True)
        n = Note(user_id=current_user.id, title=data.get("title","Untitled"),
                 content=data.get("content",""), subject=data.get("subject","General"),
                 tags=json.dumps(data.get("tags",[])))
        db.session.add(n); db.session.commit()
        return jsonify({"success": True, "id": n.id})
    ns = Note.query.filter_by(user_id=current_user.id).order_by(
        Note.is_pinned.desc(), Note.created_at.desc()).all()
    return jsonify([{"id":n.id,"title":n.title,"content":n.content[:200],"subject":n.subject,
                     "tags":json.loads(n.tags or "[]"),"is_pinned":n.is_pinned} for n in ns])


@api_bp.route("/notes/<int:note_id>", methods=["PUT","DELETE"])
@login_required
def note_detail(note_id):
    db, _, _, _, _, _, Note = get()
    n = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    if request.method == "DELETE":
        db.session.delete(n); db.session.commit(); return jsonify({"success": True})
    data = request.get_json(force=True)
    for f in ["title","content","subject","is_pinned"]:
        if f in data: setattr(n, f, data[f])
    if "tags" in data: n.tags = json.dumps(data["tags"])
    db.session.commit(); return jsonify({"success": True})


@api_bp.route("/user/profile", methods=["GET","PUT"])
@login_required
def user_profile():
    db, *_ = get()
    if request.method == "GET":
        return jsonify({"username":current_user.username,"email":current_user.email,
                        "full_name":current_user.full_name,"avatar":current_user.avatar,
                        "grade_level":current_user.grade_level,"learning_style":current_user.learning_style,
                        "subjects":current_user.get_subjects(),"xp_points":current_user.xp_points,
                        "level":current_user.level,"streak_days":current_user.streak_days,
                        "total_sessions":current_user.total_sessions,"total_questions":current_user.total_questions,
                        "total_quiz_taken":current_user.total_quiz_taken,"is_premium":current_user.is_premium,
                        "member_since":current_user.created_at.strftime("%B %Y"),
                        "xp_progress":current_user.get_xp_progress()})
    data = request.get_json(force=True)
    for f in ["full_name","grade_level","learning_style","avatar","bio"]:
        if f in data: setattr(current_user, f, data[f])
    if "subjects" in data: current_user.subjects = json.dumps(data["subjects"])
    db.session.commit(); return jsonify({"success": True})


@api_bp.route("/leaderboard")
@login_required
def leaderboard():
    _, User, *_ = get()
    top = User.query.order_by(User.xp_points.desc()).limit(20).all()
    return jsonify([{"rank":i+1,"username":u.username,"full_name":u.full_name or u.username,
                     "avatar":u.avatar,"level":u.level,"xp":u.xp_points,
                     "is_current":u.id==current_user.id} for i,u in enumerate(top)])


@api_bp.route("/user/stats")
@login_required
def user_stats():
    _, _, _, Ach, QR, *_ = get()
    ql  = QR.query.filter_by(user_id=current_user.id).all()
    avg = round(sum(q.score for q in ql)/max(len(ql),1),1)
    return jsonify({"xp":current_user.xp_points,"level":current_user.level,
                    "xp_progress":current_user.get_xp_progress(),"streak":current_user.streak_days,
                    "total_sessions":current_user.total_sessions,"total_questions":current_user.total_questions,
                    "total_quizzes":current_user.total_quiz_taken,"avg_score":avg,
                    "achievements":Ach.query.filter_by(user_id=current_user.id).count()})
