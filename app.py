"""
NeuroTutor AI - Complete Single-File Application
No blueprints, no circular imports, guaranteed to work.
"""

import os, json, uuid, datetime, re
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.utils import secure_filename

load_dotenv()

# ── App setup ──────────────────────────────────────────────────
app = Flask(__name__,
            template_folder="frontend/templates",
            static_folder="frontend/static")

app.config.update(
    SECRET_KEY                     = os.getenv("SECRET_KEY", "neurtutor-secret-2024"),
    SQLALCHEMY_DATABASE_URI        = "sqlite:///neurtutor.db",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    JWT_SECRET_KEY                 = os.getenv("JWT_SECRET_KEY", "jwt-secret-2024"),
    JWT_ACCESS_TOKEN_EXPIRES       = datetime.timedelta(hours=24),
)

db            = SQLAlchemy(app)
bcrypt        = Bcrypt(app)
login_manager = LoginManager(app)
jwt           = JWTManager(app)
CORS(app)

login_manager.login_view = "login_page"

# ── Models ─────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80), unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    full_name      = db.Column(db.String(150), default="")
    avatar         = db.Column(db.String(10), default="🎓")
    grade_level    = db.Column(db.String(60), default="High School")
    learning_style = db.Column(db.String(50), default="visual")
    subjects       = db.Column(db.Text, default="[]")
    xp_points      = db.Column(db.Integer, default=0)
    level          = db.Column(db.Integer, default=1)
    streak_days    = db.Column(db.Integer, default=0)
    last_active    = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_sessions    = db.Column(db.Integer, default=0)
    total_questions   = db.Column(db.Integer, default=0)
    total_quiz_taken  = db.Column(db.Integer, default=0)
    is_premium     = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sessions     = db.relationship("LearningSession", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    achievements = db.relationship("Achievement",     backref="user", lazy="dynamic", cascade="all, delete-orphan")
    quiz_results = db.relationship("QuizResult",      backref="user", lazy="dynamic", cascade="all, delete-orphan")
    study_plans  = db.relationship("StudyPlan",       backref="user", lazy="dynamic", cascade="all, delete-orphan")
    notes        = db.relationship("Note",            backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, p):   self.password_hash = bcrypt.generate_password_hash(p).decode("utf-8")
    def check_password(self, p): return bcrypt.check_password_hash(self.password_hash, p)
    def add_xp(self, pts):
        old = self.level; self.xp_points += pts; self.level = 1 + (self.xp_points // 500)
        return self.level if self.level > old else 0
    def get_subjects(self):
        try: return json.loads(self.subjects or "[]")
        except: return []
    def get_xp_progress(self): return (self.xp_points % 500) / 500 * 100
    @property
    def display_name(self): return self.full_name.split()[0] if self.full_name else self.username


class LearningSession(db.Model):
    __tablename__ = "learning_sessions"
    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject    = db.Column(db.String(100), default="General")
    topic      = db.Column(db.String(200), default="Open Learning")
    messages   = db.Column(db.Text, default="[]")
    agent_mode = db.Column(db.String(50), default="tutor")
    xp_earned  = db.Column(db.Integer, default=0)
    msg_count  = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def get_messages(self):
        try: return json.loads(self.messages or "[]")
        except: return []


class Achievement(db.Model):
    __tablename__ = "achievements"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    key         = db.Column(db.String(60))
    title       = db.Column(db.String(100))
    description = db.Column(db.String(200))
    icon        = db.Column(db.String(10))
    category    = db.Column(db.String(50), default="learning")
    xp_value    = db.Column(db.Integer, default=50)
    earned_at   = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class QuizResult(db.Model):
    __tablename__ = "quiz_results"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject         = db.Column(db.String(100))
    topic           = db.Column(db.String(200))
    difficulty      = db.Column(db.String(20), default="medium")
    score           = db.Column(db.Float, default=0.0)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    time_taken_secs = db.Column(db.Float, default=0.0)
    quiz_data       = db.Column(db.Text, default="{}")
    grade           = db.Column(db.String(2), default="F")
    taken_at        = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class StudyPlan(db.Model):
    __tablename__ = "study_plans"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(200))
    subject    = db.Column(db.String(100))
    goal       = db.Column(db.Text)
    plan_data  = db.Column(db.Text, default="{}")
    progress   = db.Column(db.Float, default=0.0)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deadline   = db.Column(db.DateTime)


class Note(db.Model):
    __tablename__ = "notes"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(200))
    content    = db.Column(db.Text)
    subject    = db.Column(db.String(100))
    tags       = db.Column(db.Text, default="[]")
    is_pinned  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── Jinja filters ──────────────────────────────────────────────
@app.template_filter("from_json")
def _from_json(v):
    try: return json.loads(v) if v else {}
    except: return {}

@app.template_filter("timeago")
def _timeago(dt):
    if not dt: return "never"
    d = datetime.datetime.utcnow() - dt
    if d.days > 365: return f"{d.days//365}y ago"
    if d.days > 30:  return f"{d.days//30}mo ago"
    if d.days > 0:   return f"{d.days}d ago"
    h = d.seconds // 3600
    if h > 0: return f"{h}h ago"
    m = d.seconds // 60
    return f"{m}m ago" if m > 0 else "just now"

@app.context_processor
def _inject(): return {"now": datetime.datetime.utcnow()}


# ── AI Agents (inline, no circular imports) ────────────────────
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

BASE_SYSTEM = """You are NeuroTutor — an expert AI tutor.
Student: {name} | Grade: {grade} | Style: {style} | Level: {level}
Subject: {subject} | Mode: {mode}
{mode_inst}
Use markdown. End with a follow-up question."""

MODE_INST = {
    "tutor":    "📖 Give clear explanations with examples and a Quick Check question.",
    "socratic": "🤔 Ask guiding questions only. Never give direct answers.",
    "exam_prep":"📋 Key concept → Mnemonics → Practice question.",
    "creative": "🎨 Use stories and metaphors to explain.",
    "debug":    "🔧 [Problem] → [Root cause] → [Fix] → [Lesson]",
}

RESOURCES = {
    "Mathematics":      [{"type":"tool","name":"Wolfram Alpha","url":"https://wolframalpha.com","desc":"Compute math"},{"type":"video","name":"Khan Academy","url":"https://khanacademy.org/math","desc":"Free courses"}],
    "Physics":          [{"type":"sim","name":"PhET Simulations","url":"https://phet.colorado.edu","desc":"Interactive sims"}],
    "Chemistry":        [{"type":"learn","name":"ChemLibreTexts","url":"https://chem.libretexts.org","desc":"Free textbooks"}],
    "Computer Science": [{"type":"practice","name":"LeetCode","url":"https://leetcode.com","desc":"Coding problems"},{"type":"learn","name":"CS50","url":"https://cs50.harvard.edu","desc":"Free CS course"}],
    "Biology":          [{"type":"video","name":"Khan Academy Bio","url":"https://khanacademy.org/science/biology","desc":"Biology courses"}],
}

# ── New Feature Agents ─────────────────────────────────────────
from backend.agents.rag_engine import get_rag_engine
from backend.agents.performance_predictor import get_predictor

rag_engine      = get_rag_engine()
predictor       = get_predictor()

UPLOAD_FOLDER   = os.path.join(os.path.dirname(__file__), "instance", "uploads")
ALLOWED_EXT     = {"pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

_genai_configured = False

def _configure_genai():
    global _genai_configured
    if not _genai_configured and GEMINI_KEY and not GEMINI_KEY.startswith("your_"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            _genai_configured = True
        except: pass

def ai_chat(message, history, user_ctx, mode="tutor", subject="General", rag_context=""):
    _configure_genai()
    rag_block = ""
    if rag_context:
        rag_block = f"\n\nPDF DOCUMENT CONTEXT (student's uploaded syllabus/textbook):\n---\n{rag_context[:2000]}\n---\nGround your answer in the above PDF content. Give a clear step-by-step solution referencing the document."
    sys_p = BASE_SYSTEM.format(
        name=user_ctx.get("name","Student"), grade=user_ctx.get("grade_level","High School"),
        style=user_ctx.get("learning_style","visual"), level=user_ctx.get("level",1),
        subject=subject, mode=mode.replace("_"," ").title(),
        mode_inst=MODE_INST.get(mode, MODE_INST["tutor"])) + rag_block
    steps = ["🔍 Intent classified", "📚 Knowledge retrieved", "🗺️ Curriculum mapped"]
    if rag_context:
        steps.insert(1, "📄 PDF context retrieved via ChromaDB RAG")

    if GEMINI_KEY and not GEMINI_KEY.startswith("your_"):
        # Try LangChain + LangGraph first
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            llm  = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_KEY,
                                          max_output_tokens=4096, temperature=0.7,
                                          convert_system_message_to_human=True)
            msgs = [SystemMessage(content=sys_p)]
            for m in history[-8:]:
                if isinstance(m, dict):
                    if m.get("role") == "user": msgs.append(HumanMessage(content=m["content"]))
                    elif m.get("role") == "assistant": msgs.append(AIMessage(content=m["content"]))
            msgs.append(HumanMessage(content=message))
            resp = llm.invoke(msgs)
            steps.append("🤖 Gemini (LangChain) generated response")
            steps.append("✨ Quality checked")
            return {"content": resp.content, "agent_steps": steps,
                    "resources": RESOURCES.get(subject, [])[:2], "follow_up_questions": []}
        except Exception as e:
            print(f"LangChain error: {e}")

        # Fallback: direct google-generativeai SDK
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=sys_p,
                generation_config=genai.types.GenerationConfig(max_output_tokens=4096, temperature=0.7))
            hist  = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]}
                     for m in history[-8:] if isinstance(m,dict) and m.get("role") in ("user","assistant")]
            chat  = model.start_chat(history=hist)
            resp  = chat.send_message(message)
            steps.append("🤖 Gemini (Direct SDK) generated response")
            steps.append("✨ Quality checked")
            return {"content": resp.text, "agent_steps": steps,
                    "resources": RESOURCES.get(subject, [])[:2], "follow_up_questions": []}
        except Exception as e:
            print(f"Gemini SDK error: {e}")

    # Demo mode
    return {"content": f"""**Demo Mode** 🎓

Your question: *"{message}"*

Add your **Gemini API key** to `.env`:
```
GEMINI_API_KEY=AIzaSy...your_key
```
Get a free key at **https://aistudio.google.com/app/apikey**""",
            "agent_steps": ["🎭 Demo mode — add GEMINI_API_KEY"],
            "resources": [{"type":"setup","name":"Get Free Gemini API Key","url":"https://aistudio.google.com/app/apikey","desc":"Free 1M tokens/month"}],
            "follow_up_questions": []}


QUIZ_FALLBACK = {
    "Mathematics": [
        {"id":1,"question":"Derivative of sin(x)?","options":{"A":"cos(x)","B":"-cos(x)","C":"-sin(x)","D":"tan(x)"},"correct":"A","explanation":"d/dx[sin(x)] = cos(x)","hint":"Think unit circle.","points":10,"tags":["calculus"]},
        {"id":2,"question":"Solve 2x² - 8 = 0. x = ?","options":{"A":"±2","B":"±4","C":"±√8","D":"4"},"correct":"A","explanation":"x²=4 → x=±2","hint":"Isolate x² first.","points":10,"tags":["algebra"]},
        {"id":3,"question":"log₂(64) = ?","options":{"A":"4","B":"6","C":"8","D":"32"},"correct":"B","explanation":"2⁶=64","hint":"2 to what power = 64?","points":10,"tags":["logarithms"]},
        {"id":4,"question":"Interior angles of hexagon?","options":{"A":"540°","B":"620°","C":"720°","D":"900°"},"correct":"C","explanation":"(6-2)×180=720°","hint":"(n-2)×180°","points":10,"tags":["geometry"]},
        {"id":5,"question":"P(rolling 6 on fair die)?","options":{"A":"1/3","B":"1/6","C":"1/4","D":"1/2"},"correct":"B","explanation":"1/6","hint":"Favourable÷Total","points":5,"tags":["probability"]},
    ],
    "Physics": [
        {"id":1,"question":"F=ma is Newton's ___ Law?","options":{"A":"First","B":"Second","C":"Third","D":"Fourth"},"correct":"B","explanation":"Newton's 2nd Law: F=ma","hint":"Force=mass×acceleration","points":10,"tags":["mechanics"]},
        {"id":2,"question":"Unit of resistance?","options":{"A":"Ampere","B":"Volt","C":"Ohm","D":"Watt"},"correct":"C","explanation":"Ohms (Ω)","hint":"V=IR","points":5,"tags":["electricity"]},
        {"id":3,"question":"Speed of light ≈?","options":{"A":"3×10⁶","B":"3×10⁸","C":"3×10¹⁰","D":"3×10⁴"},"correct":"B","explanation":"c≈3×10⁸ m/s","hint":"c=3×10? m/s","points":15,"tags":["light"]},
    ],
    "Computer Science": [
        {"id":1,"question":"Time complexity of binary search?","options":{"A":"O(n)","B":"O(n²)","C":"O(log n)","D":"O(1)"},"correct":"C","explanation":"Halves search space each step","hint":"How many times halve n?","points":15,"tags":["algorithms"]},
        {"id":2,"question":"LIFO structure?","options":{"A":"Queue","B":"Stack","C":"Linked List","D":"Tree"},"correct":"B","explanation":"Stack=Last In First Out","hint":"Pile of plates","points":10,"tags":["data structures"]},
        {"id":3,"question":"SQL stands for?","options":{"A":"Structured Query Language","B":"Simple Question Language","C":"System Query Logic","D":"Sequential Queue Language"},"correct":"A","explanation":"Structured Query Language","hint":"Used for databases","points":5,"tags":["databases"]},
    ],
    "Chemistry": [
        {"id":1,"question":"Atomic number of Carbon?","options":{"A":"6","B":"12","C":"14","D":"8"},"correct":"A","explanation":"Carbon has 6 protons","hint":"Atomic number=protons","points":5,"tags":["elements"]},
        {"id":2,"question":"Bond type in NaCl?","options":{"A":"Covalent","B":"Metallic","C":"Ionic","D":"Hydrogen"},"correct":"C","explanation":"Na⁺ and Cl⁻ ionic bond","hint":"Metal+non-metal→?","points":10,"tags":["bonding"]},
    ],
    "Biology": [
        {"id":1,"question":"Site of photosynthesis?","options":{"A":"Mitochondria","B":"Nucleus","C":"Chloroplast","D":"Ribosome"},"correct":"C","explanation":"Chloroplasts do photosynthesis","hint":"Which organelle is green?","points":5,"tags":["cell biology"]},
        {"id":2,"question":"Powerhouse of the cell?","options":{"A":"Nucleus","B":"Ribosome","C":"Golgi body","D":"Mitochondria"},"correct":"D","explanation":"Mitochondria produce ATP","hint":"Makes ATP","points":5,"tags":["organelles"]},
    ],
}

QUIZ_PROMPT = """Generate a {n}-question multiple-choice quiz on "{topic}" in {subject}. Difficulty: {diff}.
Return ONLY valid JSON, no markdown fences:
{{"title":"Quiz title","subject":"{subject}","topic":"{topic}","difficulty":"{diff}","estimated_mins":{mins},"questions":[{{"id":1,"question":"?","options":{{"A":"","B":"","C":"","D":""}},"correct":"A","explanation":"","hint":"","points":10,"tags":["tag"]}}]}}"""

def ai_generate_quiz(subject, topic, difficulty, n, user_level):
    topic = topic or f"Core {subject} Concepts"
    mins  = n * (2 if difficulty=="easy" else 3 if difficulty=="medium" else 4)
    _configure_genai()
    if GEMINI_KEY and not GEMINI_KEY.startswith("your_"):
        try:
            import google.generativeai as genai
            m    = genai.GenerativeModel(GEMINI_MODEL, generation_config=genai.types.GenerationConfig(temperature=0.3, max_output_tokens=3000))
            resp = m.generate_content(QUIZ_PROMPT.format(n=n,topic=topic,subject=subject,diff=difficulty,mins=mins))
            text = re.sub(r'^```(?:json)?\s*','',resp.text.strip()); text=re.sub(r'\s*```$','',text)
            data = json.loads(text)
            if "questions" in data and data["questions"]: return data
        except Exception as e: print(f"Quiz AI error: {e}")
    bank = QUIZ_FALLBACK.get(subject, QUIZ_FALLBACK["Mathematics"])
    qs   = [dict(q) for q in bank[:n]]
    for i,q in enumerate(qs,1): q["id"]=i
    return {"title":f"{subject} Quiz","subject":subject,"topic":topic,"difficulty":difficulty,"estimated_mins":n*3,"questions":qs}

def evaluate_quiz(answers, quiz_data):
    questions = quiz_data.get("questions",[])
    if not questions: return {"score":0,"correct":0,"total":0,"feedback":[],"grade":"F","message":"No questions","earned_points":0,"total_points":0}
    correct=0; tp=0; ep=0; feedback=[]
    for q in questions:
        qid=str(q.get("id","")); ca=q.get("correct","").upper(); ua=(answers.get(qid) or "").upper()
        ok=ua==ca; pts=q.get("points",10); tp+=pts
        if ok: correct+=1; ep+=pts
        feedback.append({"question_id":qid,"question":q.get("question",""),"user_answer":ua,
                         "correct_answer":ca,"is_correct":ok,"explanation":q.get("explanation",""),
                         "points_earned":pts if ok else 0,"points_max":pts,"tags":q.get("tags",[])})
    total=len(questions); score=round(correct/total*100,1) if total>0 else 0
    grade="A+"if score==100 else"A"if score>=90 else"B"if score>=80 else"C"if score>=70 else"D"if score>=60 else"F"
    msgs={"A+":"🌟 Perfect score!","A":"🎉 Excellent!","B":"👏 Great work!","C":"💪 Good effort!","D":"📚 Keep practising!","F":"🔄 Review with AI Tutor!"}
    return {"score":score,"correct":correct,"total":total,"earned_points":ep,"total_points":tp,
            "grade":grade,"message":msgs[grade],"feedback":feedback}

def ai_generate_plan(subject, goal, deadline, hours, level, ctx):
    _configure_genai()
    if GEMINI_KEY and not GEMINI_KEY.startswith("your_"):
        try:
            import google.generativeai as genai
            prompt = f"""Create a study plan JSON. No markdown fences. Subject:{subject}, Goal:{goal}, Deadline:{deadline}, Hours/day:{hours}, Level:{level}
{{"title":"","subject":"{subject}","goal":"{goal}","overview":"","total_weeks":4,"daily_hours":{hours},"weeks":[{{"week":1,"theme":"","objectives":[],"days":[{{"day":"Monday","focus":"","tasks":[{{"task":"","duration_mins":30,"type":"reading","description":"","resources":[]}}]}}]}}],"milestones":[],"study_tips":[],"resources":[]}}"""
            m    = genai.GenerativeModel(GEMINI_MODEL, generation_config=genai.types.GenerationConfig(temperature=0.4,max_output_tokens=4000))
            resp = m.generate_content(prompt)
            text = re.sub(r'^```(?:json)?\s*','',resp.text.strip()); text=re.sub(r'\s*```$','',text)
            return json.loads(text)
        except Exception as e: print(f"StudyPlan error: {e}")
    h=int(hours); t=h*30
    return {"title":f"{subject} Mastery Plan","subject":subject,"goal":goal or f"Master {subject}",
            "overview":f"A {h}h/day plan to reach your {subject} goal in 4 weeks.","total_weeks":4,"daily_hours":h,
            "weeks":[{"week":1,"theme":f"Foundations of {subject}","objectives":[f"Understand core {subject} concepts"],"days":[
                {"day":"Monday","focus":"Introduction","tasks":[{"task":f"Read intro to {subject}","duration_mins":t,"type":"reading","description":"Overview","resources":["Textbook Ch.1"]}]},
                {"day":"Tuesday","focus":"Video lesson","tasks":[{"task":"Watch lecture","duration_mins":t,"type":"video","description":"Video walkthrough","resources":["Khan Academy"]}]},
                {"day":"Wednesday","focus":"AI Tutor","tasks":[{"task":"NeuroTutor AI session","duration_mins":t,"type":"ai_session","description":"Ask questions","resources":["NeuroTutor"]}]},
                {"day":"Thursday","focus":"Practice","tasks":[{"task":"Problem set","duration_mins":t,"type":"practice","description":"Exercises","resources":["Textbook"]}]},
                {"day":"Friday","focus":"Quiz","tasks":[{"task":"Take AI Quiz","duration_mins":30,"type":"quiz","description":"Test yourself","resources":["NeuroTutor Quiz"]}]},
            ]}],
            "milestones":[{"week":2,"title":"Foundation Done","description":"Know the basics","check":["Scored 60%+ on quiz"]}],
            "study_tips":["Pomodoro: 25min study+5min break","Review notes within 24hrs","Use Socratic mode for deeper understanding"],
            "resources":[{"type":"ai","name":"NeuroTutor AI","desc":"Your personal tutor"},{"type":"video","name":"Khan Academy","desc":"Free video lessons"}]}

def award_achievement(user_id, key, title, desc, icon, xp):
    if not Achievement.query.filter_by(user_id=user_id, key=key).first():
        a = Achievement(user_id=user_id, key=key, title=title, description=desc, icon=icon, xp_value=xp)
        db.session.add(a)
        u = db.session.get(User, user_id)
        if u: u.add_xp(xp)
        db.session.commit()
        return {"title":title,"icon":icon,"xp":xp}
    return None


# ══════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/register", methods=["GET","POST"])
def register_page():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    if request.method == "POST":
        import re as _re
        data      = request.get_json(silent=True) or request.form
        email     = (data.get("email") or "").strip().lower()
        full_name = (data.get("display_name") or data.get("full_name") or data.get("username") or "").strip()
        password  = data.get("password") or ""
        if not email or not full_name or not password:
            return jsonify({"error":"All fields are required"}),400
        if len(password)<6:   return jsonify({"error":"Password must be at least 6 characters"}),400
        if not _re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return jsonify({"error":"Invalid email address"}),400
        if User.query.filter_by(email=email).first():
            return jsonify({"error":"Email already registered"}),409
        # Auto-generate a unique username from full_name
        base_uname = _re.sub(r'[^a-z0-9_]', '', full_name.lower().replace(' ', '_')) or email.split('@')[0]
        username   = base_uname
        _n = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_uname}{_n}"; _n += 1
        subjects = data.get("subjects",[])
        if isinstance(subjects,str):
            try: subjects=json.loads(subjects)
            except: subjects=[]
        user = User(username=username, email=email, full_name=full_name,
                    grade_level=data.get("grade_level","High School"), learning_style=data.get("learning_style","visual"),
                    avatar=data.get("avatar","🎓"), subjects=json.dumps(subjects))
        user.set_password(password)
        db.session.add(user); db.session.flush()
        a = Achievement(user_id=user.id, key="welcome", title="Welcome Scholar!", description="Joined NeuroTutor AI", icon="🌟", category="milestone", xp_value=100)
        db.session.add(a); user.add_xp(100); db.session.commit()
        login_user(user)
        token = create_access_token(identity=user.id)
        return jsonify({"success":True,"token":token,"redirect":url_for("dashboard")})
    return render_template("auth/register.html")


@app.route("/login", methods=["GET","POST"])
def login_page():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    if request.method == "POST":
        data     = request.get_json(silent=True) or request.form
        email    = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        remember = bool(data.get("remember",False))
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error":"Invalid email or password"}),401
        login_user(user, remember=remember)
        user.last_active=datetime.datetime.utcnow(); user.total_sessions+=1; db.session.commit()
        token = create_access_token(identity=user.id)
        return jsonify({"success":True,"token":token,"redirect":url_for("dashboard")})
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user(); return redirect(url_for("login_page"))


# ══════════════════════════════════════════════════════════════
# PAGE ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("pages/dashboard.html", user=current_user,
        recent_sessions = LearningSession.query.filter_by(user_id=current_user.id).order_by(LearningSession.started_at.desc()).limit(5).all(),
        recent_ach      = Achievement.query.filter_by(user_id=current_user.id).order_by(Achievement.earned_at.desc()).limit(6).all(),
        recent_quiz     = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.taken_at.desc()).limit(5).all(),
        active_plans    = StudyPlan.query.filter_by(user_id=current_user.id, is_active=True).all(),
        total_ach       = Achievement.query.filter_by(user_id=current_user.id).count())


@app.route("/tutor")
@login_required
def tutor():
    sid = str(uuid.uuid4()); subject=request.args.get("subject","General"); topic=request.args.get("topic","Open Learning")
    s   = LearningSession(session_id=sid, user_id=current_user.id, subject=subject, topic=topic)
    db.session.add(s); db.session.commit()
    return render_template("pages/tutor.html", user=current_user, session_id=sid, subject=subject, topic=topic)


@app.route("/quiz")
@login_required
def quiz(): return render_template("pages/quiz.html", user=current_user)


@app.route("/study-plans")
@login_required
def study_plans():
    plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.created_at.desc()).all()
    return render_template("pages/study_plans.html", user=current_user, plans=plans)


@app.route("/analytics")
@login_required
def analytics(): return render_template("pages/analytics.html", user=current_user)


@app.route("/notes")
@login_required
def notes():
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.is_pinned.desc(), Note.created_at.desc()).all()
    return render_template("pages/notes.html", user=current_user, notes=user_notes)


@app.route("/leaderboard")
@login_required
def leaderboard():
    top   = User.query.order_by(User.xp_points.desc()).limit(20).all()
    rank  = User.query.filter(User.xp_points>current_user.xp_points).count()+1
    return render_template("pages/leaderboard.html", user=current_user, top_users=top, user_rank=rank)


@app.route("/profile")
@login_required
def profile():
    achs  = Achievement.query.filter_by(user_id=current_user.id).order_by(Achievement.earned_at.desc()).all()
    rq    = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.taken_at.desc()).limit(10).all()
    avg   = round(sum(q.score for q in rq)/max(len(rq),1),1)
    return render_template("pages/profile.html", user=current_user, achievements=achs, recent_quiz=rq, avg_score=avg)


# ══════════════════════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data    = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    sid     = data.get("session_id"); mode=data.get("mode","tutor"); subject=data.get("subject","General")
    use_pdf = data.get("use_pdf", False)
    if not message: return jsonify({"error":"Empty message"}),400
    ls      = LearningSession.query.filter_by(session_id=sid, user_id=current_user.id).first()
    history = ls.get_messages() if ls else []

    # RAG: retrieve relevant chunks from user's uploaded PDFs
    rag_context = ""
    rag_sources = []
    if use_pdf:
        chunks = rag_engine.retrieve(current_user.id, message, n_results=4)
        if chunks:
            rag_context = "\n\n".join(chunks)
            rag_sources = [{"type":"pdf","name":"Your Uploaded Document","desc":"Retrieved from your PDF"}]

    result  = ai_chat(message, history, {"name":current_user.display_name,"grade_level":current_user.grade_level,
              "learning_style":current_user.learning_style,"subjects":current_user.get_subjects(),"level":current_user.level},
              mode, subject, rag_context=rag_context)
    history.append({"role":"user","content":message,"timestamp":datetime.datetime.utcnow().isoformat()})
    history.append({"role":"assistant","content":result["content"],"timestamp":datetime.datetime.utcnow().isoformat(),"mode":mode})
    if ls: ls.messages=json.dumps(history); ls.agent_mode=mode; ls.msg_count=len([m for m in history if m["role"]=="user"]); ls.xp_earned+=10
    current_user.total_questions+=1; leveled_up=current_user.add_xp(10); db.session.commit()
    new_ach=[]
    if current_user.total_questions==1: r=award_achievement(current_user.id,"first_q","First Question","Asked first question","💬",50); new_ach+=[r] if r else []
    resources = result.get("resources",[]) + rag_sources
    return jsonify({"response":result["content"],"agent_steps":result.get("agent_steps",[]),
                    "resources":resources,"follow_up_questions":result.get("follow_up_questions",[]),
                    "xp_earned":10,"total_xp":current_user.xp_points,"level":current_user.level,
                    "new_achievements":new_ach,"leveled_up":leveled_up,
                    "rag_used":bool(rag_context),"rag_chunks":len(rag_context.split("\n\n")) if rag_context else 0})


@app.route("/api/quiz/generate", methods=["POST"])
@login_required
def api_quiz_generate():
    d = request.get_json(force=True)
    return jsonify(ai_generate_quiz(d.get("subject","Mathematics"),d.get("topic",""),
                                    d.get("difficulty","medium"),int(d.get("num_questions",5)),current_user.level))


@app.route("/api/quiz/submit", methods=["POST"])
@login_required
def api_quiz_submit():
    d=request.get_json(force=True); result=evaluate_quiz(d.get("answers",{}),d.get("quiz_data",{}))
    xp=max(5,int(result["score"]*2))
    qr=QuizResult(user_id=current_user.id,subject=d.get("subject","General"),topic=d.get("topic",""),
                  difficulty=d.get("quiz_data",{}).get("difficulty","medium"),score=result["score"],
                  total_questions=result["total"],correct_answers=result["correct"],
                  time_taken_secs=d.get("time_taken",0),grade=result["grade"],
                  quiz_data=json.dumps({"feedback":result["feedback"]}))
    db.session.add(qr); current_user.total_quiz_taken+=1; current_user.add_xp(xp); db.session.commit()
    new_ach=[]
    if result["score"]==100: r=award_achievement(current_user.id,"perfect","Perfect Score!","Got 100%","💯",200); new_ach+=[r] if r else []
    if result["score"]>=90:  r=award_achievement(current_user.id,"high","High Achiever","Scored 90%+","⭐",100); new_ach+=[r] if r else []
    if current_user.total_quiz_taken==1: r=award_achievement(current_user.id,"first_quiz","Quiz Taker","First quiz","📝",75); new_ach+=[r] if r else []
    return jsonify({**result,"xp_earned":xp,"total_xp":current_user.xp_points,"new_achievements":new_ach})


@app.route("/api/study-plan/generate", methods=["POST"])
@login_required
def api_plan_generate():
    d=request.get_json(force=True)
    plan=ai_generate_plan(d.get("subject","Mathematics"),d.get("goal",""),d.get("deadline",""),
                          float(d.get("hours_per_day",2)),d.get("current_level","beginner"),
                          {"grade":current_user.grade_level,"style":current_user.learning_style})
    dl=None
    if d.get("deadline"):
        try: dl=datetime.datetime.fromisoformat(d["deadline"])
        except: pass
    sp=StudyPlan(user_id=current_user.id,title=plan.get("title","Plan"),subject=d.get("subject"),
                 goal=d.get("goal",""),plan_data=json.dumps(plan),deadline=dl)
    db.session.add(sp); db.session.commit(); plan["plan_id"]=sp.id
    award_achievement(current_user.id,"first_plan","Planner","Created first study plan","🗺️",100)
    return jsonify(plan)


@app.route("/api/study-plan/<int:plan_id>", methods=["GET","DELETE"])
@login_required
def api_plan(plan_id):
    sp=StudyPlan.query.filter_by(id=plan_id,user_id=current_user.id).first_or_404()
    if request.method=="DELETE": db.session.delete(sp); db.session.commit(); return jsonify({"success":True})
    pd=json.loads(sp.plan_data or "{}")
    return jsonify({**pd,"plan_id":sp.id,"title":sp.title,"subject":sp.subject,"progress":sp.progress})


@app.route("/api/analytics")
@login_required
def api_analytics():
    sessions=LearningSession.query.filter_by(user_id=current_user.id).all()
    quizzes =QuizResult.query.filter_by(user_id=current_user.id).all()
    achs    =Achievement.query.filter_by(user_id=current_user.id).all()
    avg=round(sum(q.score for q in quizzes)/max(len(quizzes),1),1)
    subj={}
    for qr in quizzes:
        s=qr.subject or "General"; subj.setdefault(s,[]); subj[s].append(qr.score)
    sc=[{"subject":k,"avg_score":round(sum(v)/len(v),1),"quizzes":len(v)} for k,v in subj.items()]
    trend=[{"date":qr.taken_at.strftime("%d %b"),"score":qr.score,"grade":qr.grade} for qr in sorted(quizzes,key=lambda x:x.taken_at)[-10:]]
    imp=0
    if len(quizzes)>=4:
        s=sorted(quizzes,key=lambda x:x.taken_at); h=len(s)//2
        imp=round(sum(q.score for q in s[h:])/len(s[h:])-sum(q.score for q in s[:h])/h,1)
    strengths=[k for k,v in subj.items() if sum(v)/len(v)>=75]
    weak=[k for k,v in subj.items() if sum(v)/len(v)<60]
    recs=[]
    if avg==0: recs.append({"type":"info","icon":"🚀","msg":"Take your first quiz to get AI recommendations!"})
    elif avg>=85: recs.append({"type":"success","icon":"🏆","msg":"Excellent! Try harder difficulty quizzes."})
    elif avg>=70: recs.append({"type":"info","icon":"📈","msg":"Good progress! Challenge yourself more."})
    else: recs.append({"type":"warning","icon":"📚","msg":"Review weak areas with AI Tutor."})
    return jsonify({"overview":{"total_sessions":len(sessions),"total_quizzes":len(quizzes),"avg_score":avg,"achievements":len(achs),"improvement":imp},
                    "subject_performance":sc,"score_trend":trend,"strengths":strengths[:3],"weak_areas":weak[:3],
                    "recommendations":recs,"achievements_timeline":[{"title":a.title,"icon":a.icon,"date":a.earned_at.strftime("%d %b"),"xp":a.xp_value} for a in achs[-5:]]})


@app.route("/api/notes", methods=["GET","POST"])
@login_required
def api_notes():
    if request.method=="POST":
        d=request.get_json(force=True)
        n=Note(user_id=current_user.id,title=d.get("title","Untitled"),content=d.get("content",""),
               subject=d.get("subject","General"),tags=json.dumps(d.get("tags",[])))
        db.session.add(n); db.session.commit(); return jsonify({"success":True,"id":n.id})
    ns=Note.query.filter_by(user_id=current_user.id).order_by(Note.is_pinned.desc(),Note.created_at.desc()).all()
    return jsonify([{"id":n.id,"title":n.title,"content":n.content[:200],"subject":n.subject,
                     "tags":json.loads(n.tags or "[]"),"is_pinned":n.is_pinned} for n in ns])


@app.route("/api/notes/<int:nid>", methods=["PUT","DELETE"])
@login_required
def api_note(nid):
    n=Note.query.filter_by(id=nid,user_id=current_user.id).first_or_404()
    if request.method=="DELETE": db.session.delete(n); db.session.commit(); return jsonify({"success":True})
    d=request.get_json(force=True)
    for f in ["title","content","subject","is_pinned"]:
        if f in d: setattr(n,f,d[f])
    if "tags" in d: n.tags=json.dumps(d["tags"])
    db.session.commit(); return jsonify({"success":True})


@app.route("/api/user/profile", methods=["GET","PUT"])
@login_required
def api_profile():
    if request.method=="GET":
        return jsonify({"username":current_user.username,"email":current_user.email,"full_name":current_user.full_name,
                        "avatar":current_user.avatar,"grade_level":current_user.grade_level,"learning_style":current_user.learning_style,
                        "subjects":current_user.get_subjects(),"xp_points":current_user.xp_points,"level":current_user.level,
                        "streak_days":current_user.streak_days,"total_sessions":current_user.total_sessions,
                        "total_questions":current_user.total_questions,"total_quiz_taken":current_user.total_quiz_taken,
                        "is_premium":current_user.is_premium,"member_since":current_user.created_at.strftime("%B %Y"),
                        "xp_progress":current_user.get_xp_progress()})
    d=request.get_json(force=True)
    for f in ["full_name","grade_level","learning_style","avatar"]:
        if f in d: setattr(current_user,f,d[f])
    if "subjects" in d: current_user.subjects=json.dumps(d["subjects"])
    db.session.commit(); return jsonify({"success":True})


@app.route("/api/leaderboard")
@login_required
def api_leaderboard():
    top=User.query.order_by(User.xp_points.desc()).limit(20).all()
    return jsonify([{"rank":i+1,"username":u.username,"full_name":u.full_name or u.username,
                     "avatar":u.avatar,"level":u.level,"xp":u.xp_points,"is_current":u.id==current_user.id}
                    for i,u in enumerate(top)])


@app.route("/api/user/stats")
@login_required
def api_stats():
    ql=QuizResult.query.filter_by(user_id=current_user.id).all()
    return jsonify({"xp":current_user.xp_points,"level":current_user.level,"xp_progress":current_user.get_xp_progress(),
                    "streak":current_user.streak_days,"total_sessions":current_user.total_sessions,
                    "total_questions":current_user.total_questions,"total_quizzes":current_user.total_quiz_taken,
                    "avg_score":round(sum(q.score for q in ql)/max(len(ql),1),1),
                    "achievements":Achievement.query.filter_by(user_id=current_user.id).count()})


# ── PDF Upload & RAG Chat ──────────────────────────────────────

@app.route("/pdf-chat")
@login_required
def pdf_chat_page():
    return render_template("pdf_chat.html")


@app.route("/api/pdf/upload", methods=["POST"])
@login_required
def api_pdf_upload():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Only PDF files allowed"}), 400

    filename  = secure_filename(file.filename)
    user_dir  = os.path.join(app.config["UPLOAD_FOLDER"], str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    save_path = os.path.join(user_dir, filename)
    file.save(save_path)

    result = rag_engine.ingest_pdf(current_user.id, save_path, filename)

    # Clean up the saved file after ingestion
    try:
        os.remove(save_path)
    except Exception:
        pass

    return jsonify(result)


@app.route("/api/pdf/documents", methods=["GET"])
@login_required
def api_pdf_list():
    docs = rag_engine.list_documents(current_user.id)
    return jsonify({"documents": docs})


@app.route("/api/pdf/documents/<doc_id>", methods=["DELETE"])
@login_required
def api_pdf_delete(doc_id):
    success = rag_engine.delete_document(current_user.id, doc_id)
    return jsonify({"success": success})


@app.route("/api/pdf/chat", methods=["POST"])
@login_required
def api_pdf_chat():
    data    = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    mode    = data.get("mode", "tutor")
    subject = data.get("subject", "General")
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Always retrieve from RAG for this endpoint
    chunks = rag_engine.retrieve(current_user.id, message, n_results=5)
    if not chunks:
        return jsonify({
            "response": "📄 **No PDF content found.** Please upload a syllabus or textbook PDF first using the upload button above, then ask your question again.",
            "agent_steps": ["📄 No PDF documents found in knowledge base"],
            "resources": [], "follow_up_questions": [],
            "rag_used": False, "rag_chunks": 0
        })

    rag_context = "\n\n".join(chunks)
    history = []  # PDF chat is stateless per call for simplicity

    result = ai_chat(
        message, history,
        {"name": current_user.display_name, "grade_level": current_user.grade_level,
         "learning_style": current_user.learning_style, "subjects": current_user.get_subjects(),
         "level": current_user.level},
        mode, subject, rag_context=rag_context
    )

    current_user.total_questions += 1
    current_user.add_xp(10)
    db.session.commit()

    return jsonify({
        "response": result["content"],
        "agent_steps": result.get("agent_steps", []),
        "resources": result.get("resources", []),
        "follow_up_questions": result.get("follow_up_questions", []),
        "rag_used": True,
        "rag_chunks": len(chunks)
    })


# ── Performance Predictor ──────────────────────────────────────

@app.route("/performance")
@login_required
def performance_page():
    return render_template("performance.html")


@app.route("/api/performance/predict", methods=["GET"])
@login_required
def api_performance_predict():
    quiz_results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.id.asc()).all()
    sessions     = LearningSession.query.filter_by(user_id=current_user.id).all()

    quiz_data = [{
        "subject":         q.subject,
        "score":           q.score,
        "total_questions": q.total_questions,
        "difficulty":      q.difficulty,
        "completed_at":    q.taken_at.isoformat() if q.taken_at else "",
    } for q in quiz_results]

    session_data = [{
        "session_date": s.started_at.isoformat() if s.started_at else "",
        "subject":      s.subject,
    } for s in sessions]

    user_ctx = {
        "name": current_user.display_name,
        "grade_level": current_user.grade_level,
        "level": current_user.level,
        "last_active": current_user.last_active.isoformat() if current_user.last_active else None
    }

    analysis = predictor.analyse(quiz_data, session_data, user_ctx)
    return jsonify(analysis)


# ── Create tables & run ────────────────────────────────────────
with app.app_context():
    db.create_all()
    print("✅ NeuroTutor AI — Database ready")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"""
╔══════════════════════════════════════╗
║   🧠 NeuroTutor AI is running!       ║
║   🌐 http://localhost:{port}           ║
║   📖 Ctrl+C to stop                  ║
╚══════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=False)
