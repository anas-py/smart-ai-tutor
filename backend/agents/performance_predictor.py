"""
AI Tutor — Performance Predictor
Random Forest multi-feature model for student quiz score prediction.

Model: RandomForestRegressor (sklearn)
Fallback: Exponential Weighted Moving Average (when data is scarce)

Features used per training sample:
  last_score, last3_avg, all_avg, trend, std_dev, momentum,
  attempts, days_since_last, difficulty_score, subject_id
"""

import os
import json
import statistics
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

try:
    import google.generativeai as genai
    GENAI_OK = True
except ImportError:
    GENAI_OK = False

try:
    from sklearn.ensemble import RandomForestRegressor
    RF_OK = True
except ImportError:
    RF_OK = False


# ── Constants ──────────────────────────────────────────────────────────────────

DIFFICULTY_MAP = {"easy": 1.0, "medium": 2.0, "hard": 3.0}

SUBJECT_LIST = [
    "Mathematics", "Physics", "Chemistry", "Biology",
    "Computer Science", "English", "History", "Geography",
    "Economics", "General"
]
SUBJECT_MAP = {s: float(i) for i, s in enumerate(SUBJECT_LIST)}


# ── Subject-level aggregation ──────────────────────────────────────────────────

def _compute_topic_scores(quiz_results: List[dict]) -> Dict[str, dict]:
    """Aggregate scores per subject. Returns {subject: {avg_score, attempts, trend, ...}}"""
    subject_data: Dict[str, List[dict]] = defaultdict(list)
    for qr in quiz_results:
        subj  = qr.get("subject", "General")
        # score is already stored as a percentage (0–100) by evaluate_quiz()
        pct = float(qr.get("score", 0))
        subject_data[subj].append({"pct": pct, "date": qr.get("completed_at", "")})

    result = {}
    for subj, entries in subject_data.items():
        scores = [e["pct"] for e in entries]
        avg    = sum(scores) / len(scores)
        mid    = len(scores) // 2
        if mid > 0:
            first_h  = sum(scores[:mid]) / mid
            second_h = sum(scores[mid:]) / max(len(scores) - mid, 1)
            trend = ("improving" if second_h > first_h + 5 else
                     "declining" if second_h < first_h - 5 else "stable")
        else:
            trend = "new"

        result[subj] = {
            "avg_score":    round(avg, 1),
            "attempts":     len(scores),
            "trend":        trend,
            "weak":         avg < 60,
            "mastery":      ("expert"     if avg >= 85 else
                             "proficient" if avg >= 70 else
                             "developing" if avg >= 50 else "needs_work"),
            "recent_score": round(scores[-1], 1) if scores else 0,
        }
    return result


# ── Streak risk ────────────────────────────────────────────────────────────────

def _compute_streak_risk(last_active: Optional[str]) -> dict:
    if not last_active:
        return {"risk": "unknown", "days_inactive": 0,
                "message": "No activity recorded yet."}
    try:
        if isinstance(last_active, str):
            last_dt = datetime.fromisoformat(
                last_active.replace("Z", "+00:00").split("+")[0])
        else:
            last_dt = last_active
        days_inactive = (datetime.utcnow() - last_dt).days
    except Exception:
        days_inactive = 0

    if days_inactive == 0:
        return {"risk": "low",      "days_inactive": 0,
                "message": "You studied today — great consistency!"}
    elif days_inactive == 1:
        return {"risk": "medium",   "days_inactive": 1,
                "message": "Study today to keep your streak alive!"}
    elif days_inactive <= 3:
        return {"risk": "high",     "days_inactive": days_inactive,
                "message": f"⚠️ {days_inactive} days inactive — streak at risk!"}
    else:
        return {"risk": "critical", "days_inactive": days_inactive,
                "message": f"🔴 {days_inactive} days inactive — get back on track!"}


# ── EWMA fallback ──────────────────────────────────────────────────────────────

def _predict_ewma(scores: List[float], alpha: float = 0.4) -> float:
    """
    Exponential Weighted Moving Average with damped trend projection.
    Used when quiz history is too short for Random Forest (< 3 training samples).
    Recent scores are weighted more heavily than old ones (controlled by alpha).
    """
    ewma = scores[0]
    for s in scores[1:]:
        ewma = alpha * s + (1 - alpha) * ewma
    # Damped trend: project slightly in the direction of recent momentum
    trend = (scores[-1] - scores[-2]) * 0.3 if len(scores) >= 2 else 0.0
    return round(float(min(max(ewma + trend, 0), 100)), 1)


# ── Feature engineering ────────────────────────────────────────────────────────

def _days_since(date_str: str) -> float:
    """Days elapsed since an ISO date string. Returns 7.0 if unparseable."""
    if not date_str:
        return 7.0
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00").split("+")[0])
        return max(0.0, (datetime.utcnow() - dt).total_seconds() / 86400.0)
    except Exception:
        return 7.0


def _build_feature_vector(
    scores:      List[float],
    difficulties: List[str],
    dates:       List[str],
    subject:     str,
) -> List[float]:
    """
    10-dimensional feature vector for one training/prediction sample.

    Idx  Feature           Description
    ---  -------           -----------
      0  last_score        Score on most recent quiz
      1  last3_avg         Average of last 3 scores  (recency)
      2  all_avg           Overall subject average    (baseline)
      3  trend             (last − first) / (n−1)    (direction of change)
      4  std_dev           Std-dev of all scores      (consistency)
      5  momentum          last3_avg − all_avg        (recent vs baseline)
      6  attempts          Number of quizzes so far   (experience)
      7  days_since_last   Days since last quiz        (freshness)
      8  difficulty_score  Encoded difficulty (1/2/3)  (task load)
      9  subject_id        Encoded subject (0-9)       (domain signal)
    """
    n         = len(scores)
    last3     = scores[-min(3, n):]
    last3_avg = sum(last3) / len(last3)
    all_avg   = sum(scores) / n
    trend     = (scores[-1] - scores[0]) / max(n - 1, 1)
    std_dev   = statistics.stdev(scores) if n >= 2 else 0.0
    momentum  = last3_avg - all_avg

    days      = _days_since(dates[-1]) if dates else 7.0
    diff_val  = DIFFICULTY_MAP.get(difficulties[-1] if difficulties else "medium", 2.0)
    subj_id   = SUBJECT_MAP.get(subject, float(len(SUBJECT_MAP)))

    return [
        scores[-1],  # last_score
        last3_avg,   # last3_avg
        all_avg,     # all_avg
        trend,       # trend
        std_dev,     # std_dev
        momentum,    # momentum
        float(n),    # attempts
        days,        # days_since_last
        diff_val,    # difficulty_score
        subj_id,     # subject_id
    ]


# ── Random Forest predictor ────────────────────────────────────────────────────

def _predict_with_rf(
    target_subject: str,
    target_scores:  List[float],
    target_meta:    List[dict],
    all_quiz_results: List[dict],
) -> Optional[float]:
    """
    Train a RandomForestRegressor on the user's full quiz history (all subjects
    pooled together) and predict the next score for target_subject.

    Training strategy — sliding window:
        For each subject with N quizzes, generate N-1 samples:
            sample i : features from quizzes [0..i-1], target = score[i]
        Pooling all subjects maximises training data and lets the model learn
        cross-subject patterns (e.g. consistency correlates with performance).

    Falls back to EWMA when total training samples < 3.
    """
    if not RF_OK:
        return _predict_ewma(target_scores)

    # ── Build training dataset from ALL subjects ───────────────────────────────
    X_train: List[List[float]] = []
    y_train: List[float]       = []

    by_subject: Dict[str, List[dict]] = defaultdict(list)
    for qr in all_quiz_results:
        by_subject[qr.get("subject", "General")].append(qr)

    for subj, records in by_subject.items():
        pcts, diffs, dates = [], [], []
        for r in records:
            # score is already a percentage — do NOT divide by total_questions again
            pct = float(r.get("score", 0))
            pcts.append(pct)
            diffs.append(r.get("difficulty", "medium"))
            dates.append(r.get("completed_at", ""))

        # Generate sliding-window training samples for this subject
        for i in range(1, len(pcts)):
            feats = _build_feature_vector(pcts[:i], diffs[:i], dates[:i], subj)
            X_train.append(feats)
            y_train.append(pcts[i])

    if len(X_train) < 3:
        # Too little history to train reliably — use EWMA
        return _predict_ewma(target_scores)

    # ── Train Random Forest ────────────────────────────────────────────────────
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=6,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    # ── Predict next score for target subject ──────────────────────────────────
    diffs_t = [m.get("difficulty", "medium") for m in target_meta]
    dates_t = [m.get("completed_at", "")     for m in target_meta]
    feats   = _build_feature_vector(target_scores, diffs_t, dates_t, target_subject)
    pred    = rf.predict([feats])[0]

    return round(float(min(max(pred, 0), 100)), 1)


# ── AI recommendations ─────────────────────────────────────────────────────────

def _generate_ai_recommendations(api_key: str, model_name: str, summary: dict) -> str:
    if not api_key or api_key.startswith("your_") or not GENAI_OK:
        return _fallback_recommendations(summary)
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        prompt = f"""You are an expert educational analyst. Based on this student's
performance data, provide specific, actionable learning recommendations.

STUDENT PERFORMANCE SUMMARY:
- Total Quizzes: {summary.get('total_quizzes', 0)}
- Overall Average Score: {summary.get('overall_avg', 0):.1f}%
- Streak Risk: {summary.get('streak_risk', {}).get('risk', 'unknown')}
- Days Inactive: {summary.get('streak_risk', {}).get('days_inactive', 0)}

SUBJECT PERFORMANCE:
{json.dumps(summary.get('subject_scores', {}), indent=2)}

WEAK SUBJECTS (score < 60%):   {', '.join(summary.get('weak_subjects', [])) or 'None'}
STRONG SUBJECTS (score >= 85%): {', '.join(summary.get('strong_subjects', [])) or 'None'}

PREDICTED NEXT SCORES (Random Forest model):
{json.dumps(summary.get('predictions', {}), indent=2)}

Provide exactly 4 recommendations in this format:
1. [Priority action for weakest subject]
2. [Study consistency recommendation]
3. [Next topic to focus on]
4. [Motivational insight based on trends]

Keep each recommendation to 1-2 sentences. Be specific, not generic.
Use the actual subject names and predicted scores where relevant."""
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"AI recommendations error: {e}")
        return _fallback_recommendations(summary)


def _fallback_recommendations(summary: dict) -> str:
    weak   = summary.get("weak_subjects", [])
    strong = summary.get("strong_subjects", [])
    avg    = summary.get("overall_avg", 0)
    preds  = summary.get("predictions", {})

    lines = []
    if weak:
        pred_note = f" (predicted next score: {preds.get(weak[0], '?')}%)" if weak[0] in preds else ""
        lines.append(f"1. Focus your next 3 sessions on **{weak[0]}**{pred_note} — "
                     f"targeted practice on weak areas compounds quickly.")
    else:
        lines.append("1. You're performing well — try increasing quiz difficulty to challenge yourself further.")

    lines.append("2. Study daily to build a consistent habit — even 15 minutes a day "
                 "compounds significantly over time.")

    if strong:
        lines.append(f"3. You excel at **{strong[0]}** — explore advanced topics or "
                     f"use it to strengthen adjacent subjects.")
    else:
        lines.append("3. Take a quiz in your weakest subject this week and review "
                     "every incorrect answer carefully.")

    if avg >= 75:
        lines.append("4. Your performance trend is positive — set a target of 90%+ "
                     "in your next quiz and maintain the momentum!")
    else:
        lines.append("4. Improvement comes from deliberate practice on weak areas, "
                     "not just repeating what you already know.")

    return "\n".join(lines)


# ── Main predictor class ───────────────────────────────────────────────────────

class PerformancePredictor:
    """
    Predicts student performance using a Random Forest model trained on the
    student's own quiz history. Falls back to EWMA for sparse data.
    """

    def __init__(self):
        self.api_key    = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def analyse(
        self,
        quiz_results:  List[dict],
        sessions:      List[dict],
        user_context:  dict,
    ) -> dict:
        """
        Full performance analysis with Random Forest score prediction.

        Args:
            quiz_results : list of dicts with keys:
                           subject, score, total_questions, difficulty, completed_at
            sessions     : list of dicts with key: session_date
            user_context : dict with keys: name, grade_level, level, last_active

        Returns:
            dict with overall stats, per-subject scores, RF predictions,
            streak risk, mastery distribution, and AI recommendations.
        """
        # ── Subject-level analysis ─────────────────────────────────────────────
        subject_scores = _compute_topic_scores(quiz_results)

        # ── Overall stats ──────────────────────────────────────────────────────
        # score is already stored as a percentage — no conversion needed
        all_scores = [float(qr.get("score", 0)) for qr in quiz_results]
        overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

        # ── Weak / strong classification ───────────────────────────────────────
        weak_subjects   = [s for s, d in subject_scores.items() if d["weak"]]
        strong_subjects = [s for s, d in subject_scores.items() if d["avg_score"] >= 85]

        # ── Streak risk ────────────────────────────────────────────────────────
        streak_risk = _compute_streak_risk(user_context.get("last_active"))

        # ── Random Forest score prediction per subject ─────────────────────────
        # Group quiz results by subject (preserve chronological order)
        by_subject: Dict[str, List[dict]] = defaultdict(list)
        for qr in quiz_results:
            by_subject[qr.get("subject", "General")].append(qr)

        predictions: Dict[str, float] = {}
        model_used:  Dict[str, str]   = {}

        for subj, records in by_subject.items():
            # score is already a percentage — do NOT divide by total_questions again
            pcts = [float(r.get("score", 0)) for r in records]
            if len(pcts) < 2:
                continue  # need at least 2 data points

            total_samples = sum(
                max(len(recs) - 1, 0)
                for recs in by_subject.values()
            )

            if total_samples >= 3 and RF_OK:
                # Enough history — use Random Forest
                pred = _predict_with_rf(subj, pcts, records, quiz_results)
                used = "Random Forest"
            else:
                # Sparse data — use EWMA
                pred = _predict_ewma(pcts)
                used = "EWMA (sparse data)"

            if pred is not None:
                predictions[subj] = pred
                model_used[subj]  = used

        # ── Session frequency (last 30 days) ───────────────────────────────────
        session_days: set = set()
        for s in sessions:
            date_str = s.get("session_date", "")
            if date_str:
                try:
                    dt = datetime.fromisoformat(str(date_str))
                    session_days.add(dt.date())
                except Exception:
                    pass
        today            = datetime.utcnow().date()
        active_last_30   = sum(1 for d in session_days if (today - d).days <= 30)

        # ── Mastery distribution ───────────────────────────────────────────────
        mastery_dist: Dict[str, int] = defaultdict(int)
        for d in subject_scores.values():
            mastery_dist[d["mastery"]] += 1

        # ── AI recommendations ─────────────────────────────────────────────────
        summary = {
            "total_quizzes":  len(quiz_results),
            "overall_avg":    overall_avg,
            "subject_scores": subject_scores,
            "weak_subjects":  weak_subjects,
            "strong_subjects": strong_subjects,
            "streak_risk":    streak_risk,
            "predictions":    predictions,
        }
        recommendations = _generate_ai_recommendations(
            self.api_key, self.model_name, summary
        )

        return {
            "overall_avg":          overall_avg,
            "total_quizzes":        len(quiz_results),
            "subject_scores":       subject_scores,
            "weak_subjects":        weak_subjects,
            "strong_subjects":      strong_subjects,
            "streak_risk":          streak_risk,
            "predicted_scores":     predictions,
            "prediction_model":     model_used,
            "active_days_last_30":  active_last_30,
            "mastery_distribution": dict(mastery_dist),
            "ai_recommendations":   recommendations,
            "performance_grade": (
                "A" if overall_avg >= 85 else
                "B" if overall_avg >= 70 else
                "C" if overall_avg >= 55 else
                "D" if overall_avg >= 40 else "F"
            ),
            "priority_subject": (
                weak_subjects[0] if weak_subjects else
                strong_subjects[0] if strong_subjects else None
            ),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_predictor: Optional[PerformancePredictor] = None


def get_predictor() -> PerformancePredictor:
    global _predictor
    if _predictor is None:
        _predictor = PerformancePredictor()
    return _predictor
