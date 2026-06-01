"""
Analytics Agent — deep learning insights and achievement system.
"""

from datetime import datetime, timedelta


# ── Achievement Definitions ─────────────────────────────────────────────────────
ACHIEVEMENT_DEFS = [
    # Onboarding
    {"key":"welcome",        "title":"Welcome Scholar!",    "icon":"🌟","desc":"Joined NeuroTutor AI",                 "xp":100,"cat":"milestone"},
    {"key":"first_question", "title":"First Question",      "icon":"💬","desc":"Asked your first question",             "xp":50, "cat":"learning"},
    {"key":"first_quiz",     "title":"Quiz Taker",          "icon":"📝","desc":"Completed your first quiz",            "xp":75, "cat":"quiz"},
    {"key":"first_plan",     "title":"Planner",             "icon":"🗺️","desc":"Created your first study plan",        "xp":100,"cat":"planning"},
    # Quiz achievements
    {"key":"perfect_score",  "title":"Perfect Score!",      "icon":"💯","desc":"Got 100% on a quiz",                   "xp":200,"cat":"quiz"},
    {"key":"quiz_5",         "title":"Quiz Enthusiast",     "icon":"🧠","desc":"Completed 5 quizzes",                  "xp":150,"cat":"quiz"},
    {"key":"quiz_20",        "title":"Quiz Master",         "icon":"🏆","desc":"Completed 20 quizzes",                 "xp":300,"cat":"quiz"},
    {"key":"high_scorer",    "title":"High Achiever",       "icon":"⭐","desc":"Scored 90%+ on a quiz",               "xp":150,"cat":"quiz"},
    # Learning streak
    {"key":"streak_3",       "title":"3-Day Streak",        "icon":"🔥","desc":"Studied 3 days in a row",              "xp":100,"cat":"streak"},
    {"key":"streak_7",       "title":"Week Warrior",        "icon":"🔥","desc":"Studied 7 days in a row",              "xp":250,"cat":"streak"},
    {"key":"streak_30",      "title":"Monthly Champion",    "icon":"🔥","desc":"Studied 30 days in a row",             "xp":500,"cat":"streak"},
    # XP / Levels
    {"key":"level_5",        "title":"Rising Scholar",      "icon":"📈","desc":"Reached Level 5",                      "xp":100,"cat":"milestone"},
    {"key":"level_10",       "title":"Knowledge Seeker",    "icon":"🎓","desc":"Reached Level 10",                     "xp":200,"cat":"milestone"},
    {"key":"xp_1000",        "title":"XP Milestone",        "icon":"💎","desc":"Earned 1,000 XP total",               "xp":100,"cat":"milestone"},
    # Sessions
    {"key":"sessions_10",    "title":"Dedicated Learner",   "icon":"📚","desc":"Completed 10 AI sessions",             "xp":150,"cat":"learning"},
    {"key":"sessions_50",    "title":"Knowledge Hunter",    "icon":"🦁","desc":"Completed 50 AI sessions",             "xp":300,"cat":"learning"},
    # Subjects
    {"key":"multi_subject",  "title":"Multi-Disciplinary",  "icon":"🌐","desc":"Studied 3+ different subjects",        "xp":200,"cat":"learning"},
    {"key":"night_owl",      "title":"Night Owl",           "icon":"🦉","desc":"Studied past midnight",                "xp":75, "cat":"fun"},
    {"key":"early_bird",     "title":"Early Bird",          "icon":"🌅","desc":"Studied before 7am",                   "xp":75, "cat":"fun"},
]


class AnalyticsAgent:

    def get_user_analytics(self, user_id, sessions, quiz_results, achievements) -> dict:
        """Compute comprehensive analytics for a user."""
        total_sessions = len(list(sessions))
        quiz_list      = list(quiz_results)
        ach_list       = list(achievements)

        total_quizzes  = len(quiz_list)
        avg_score      = round(sum(q.score for q in quiz_list) / max(len(quiz_list),1), 1)
        improvement    = self._calc_improvement(quiz_list)

        # Subject breakdown
        subj_perf = {}
        for qr in quiz_list:
            s = qr.subject or "General"
            subj_perf.setdefault(s, {"scores":[],"count":0})
            subj_perf[s]["scores"].append(qr.score)
            subj_perf[s]["count"] += 1

        subject_chart = [
            {
                "subject":    k,
                "avg_score":  round(sum(v["scores"])/max(len(v["scores"]),1), 1),
                "quizzes":    v["count"],
                "trend":      "up" if len(v["scores"])>1 and v["scores"][-1]>v["scores"][0] else "flat",
            }
            for k, v in subj_perf.items()
        ]

        # Score trend (last 15 quizzes)
        sorted_quizzes = sorted(quiz_list, key=lambda x: x.taken_at)
        score_trend = [
            {"date": qr.taken_at.strftime("%d %b"), "score": qr.score,
             "subject": qr.subject or "General", "grade": qr.grade}
            for qr in sorted_quizzes[-15:]
        ]

        # Activity heatmap (last 60 days)
        activity = {}
        all_sessions = list(sessions)
        for s in all_sessions:
            if s.started_at:
                key = s.started_at.strftime("%Y-%m-%d")
                activity[key] = activity.get(key, 0) + 1

        # Strengths & weaknesses
        strengths   = [k for k,v in subj_perf.items() if v["scores"] and sum(v["scores"])/len(v["scores"]) >= 75]
        weak_areas  = [k for k,v in subj_perf.items() if v["scores"] and sum(v["scores"])/len(v["scores"]) < 65]

        return {
            "overview": {
                "total_sessions": total_sessions,
                "total_quizzes":  total_quizzes,
                "avg_score":      avg_score,
                "achievements":   len(ach_list),
                "improvement":    improvement,
            },
            "subject_performance": subject_chart,
            "score_trend":   score_trend,
            "activity_heatmap": [{"date":k,"count":v} for k,v in sorted(activity.items())[-60:]],
            "strengths":     strengths[:4],
            "weak_areas":    weak_areas[:4],
            "achievements_timeline": [
                {"title":a.title,"icon":a.icon,"date":a.earned_at.strftime("%d %b"),"xp":a.xp_value}
                for a in sorted(ach_list, key=lambda x: x.earned_at, reverse=True)[:8]
            ],
            "recommendations": self._recommendations(avg_score, total_sessions, subj_perf, quiz_list),
            "performance_grade": self._overall_grade(avg_score, improvement, total_sessions),
        }

    def _calc_improvement(self, quiz_list):
        if len(quiz_list) < 4:
            return 0.0
        sorted_q   = sorted(quiz_list, key=lambda x: x.taken_at)
        half       = len(sorted_q) // 2
        first_avg  = sum(q.score for q in sorted_q[:half]) / half
        second_avg = sum(q.score for q in sorted_q[half:]) / (len(sorted_q)-half)
        return round(second_avg - first_avg, 1)

    def _recommendations(self, avg_score, sessions, subj_perf, quiz_list):
        recs = []
        if avg_score == 0:
            recs.append({"type":"info","icon":"🚀","msg":"Take your first quiz to get personalized AI recommendations!"})
        elif avg_score >= 85:
            recs.append({"type":"success","icon":"🏆","msg":"Outstanding performance! Try teaching concepts to others — it deepens understanding."})
        elif avg_score >= 70:
            recs.append({"type":"info","icon":"📈","msg":"You're progressing well! Challenge yourself with harder difficulty quizzes."})
        else:
            recs.append({"type":"warning","icon":"📚","msg":"Review core concepts with the AI Tutor before tackling more quizzes."})

        if sessions < 3:
            recs.append({"type":"info","icon":"🔥","msg":"Consistency is key — aim for at least one AI session every day."})

        if subj_perf:
            weak = [k for k,v in subj_perf.items() if v["scores"] and sum(v["scores"])/len(v["scores"]) < 60]
            if weak:
                recs.append({"type":"warning","icon":"🎯","msg":f"Focus on: {', '.join(weak[:2])}. Use Exam Prep mode to target weak areas."})

        if len(subj_perf) < 2:
            recs.append({"type":"info","icon":"🌐","msg":"Explore a new subject! Multi-disciplinary knowledge boosts problem-solving."})

        return recs[:4]

    def _overall_grade(self, avg_score, improvement, sessions):
        if sessions == 0: return {"grade":"—","label":"No data yet","color":"#94a3b8"}
        score = avg_score + max(improvement, 0) * 2
        if score >= 90: return {"grade":"A+","label":"Exceptional","color":"#6366f1"}
        if score >= 80: return {"grade":"A","label":"Excellent","color":"#10b981"}
        if score >= 70: return {"grade":"B","label":"Good","color":"#06b6d4"}
        if score >= 60: return {"grade":"C","label":"Fair","color":"#f59e0b"}
        return {"grade":"D","label":"Needs Work","color":"#ef4444"}


class AchievementEngine:
    """Checks conditions and awards achievements."""

    def __init__(self, db, User, Achievement):
        self.db          = db
        self.User        = User
        self.Achievement = Achievement

    def check_and_award(self, user_id: int, event: str, data: dict = None) -> list:
        """Return list of newly awarded achievements."""
        user   = self.User.query.get(user_id)
        if not user:
            return []

        awarded = []
        data    = data or {}

        # Helper to award
        def award(key):
            defn = next((d for d in ACHIEVEMENT_DEFS if d["key"]==key), None)
            if not defn:
                return
            exists = self.Achievement.query.filter_by(user_id=user_id, key=key).first()
            if exists:
                return
            ach = self.Achievement(
                user_id=user_id, key=key, title=defn["title"],
                description=defn["desc"], icon=defn["icon"],
                category=defn["cat"], xp_value=defn["xp"],
            )
            self.db.session.add(ach)
            user.add_xp(defn["xp"])
            awarded.append({"title": defn["title"], "icon": defn["icon"], "xp": defn["xp"]})

        # Event-based checks
        if event == "register":
            award("welcome")

        if event == "question":
            if user.total_questions == 1:
                award("first_question")
            if user.total_sessions >= 10:
                award("sessions_10")
            if user.total_sessions >= 50:
                award("sessions_50")

        if event == "quiz_complete":
            score = data.get("score", 0)
            if user.total_quiz_taken == 1:
                award("first_quiz")
            if score == 100:
                award("perfect_score")
            if score >= 90:
                award("high_scorer")
            if user.total_quiz_taken >= 5:
                award("quiz_5")
            if user.total_quiz_taken >= 20:
                award("quiz_20")

        if event == "study_plan":
            award("first_plan")

        if event == "level_up":
            lvl = data.get("level", 0)
            if lvl >= 5:
                award("level_5")
            if lvl >= 10:
                award("level_10")

        if event == "xp_check":
            if user.xp_points >= 1000:
                award("xp_1000")

        # Subject diversity
        from sqlalchemy import text
        subjects = self.db.session.execute(
            text("SELECT DISTINCT subject FROM quiz_results WHERE user_id=:uid"),
            {"uid": user_id}
        ).fetchall()
        if len(subjects) >= 3:
            award("multi_subject")

        # Time-based
        now = datetime.utcnow()
        if now.hour >= 0 and now.hour < 4:
            award("night_owl")
        if now.hour < 7:
            award("early_bird")

        if awarded:
            self.db.session.commit()

        return awarded
