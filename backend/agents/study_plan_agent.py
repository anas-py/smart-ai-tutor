"""Study Plan Agent — Google Gemini powered"""
import os, json, re

try:
    import google.generativeai as genai
    GENAI_OK = True
except ImportError:
    GENAI_OK = False

PLAN_PROMPT = """Create a personalized study plan. Return ONLY valid JSON, no markdown.

Subject: {subject}, Goal: {goal}, Deadline: {deadline}
Hours/day: {hours}, Current level: {level}, Grade: {grade}, Style: {style}

{{
  "title": "Plan title",
  "subject": "{subject}",
  "goal": "{goal}",
  "overview": "2-3 sentence overview",
  "total_weeks": 4,
  "daily_hours": {hours},
  "weeks": [
    {{
      "week": 1, "theme": "Week theme",
      "objectives": ["Obj 1", "Obj 2"],
      "days": [
        {{
          "day": "Monday", "focus": "What to study",
          "tasks": [{{"task":"Task name","duration_mins":30,"type":"reading","description":"Brief desc","resources":["Resource"]}}]
        }}
      ]
    }}
  ],
  "milestones": [{{"week":2,"title":"Milestone","description":"What this means","check":["Check 1"]}}],
  "study_tips": ["Tip 1","Tip 2","Tip 3"],
  "resources": [{{"type":"book","name":"Resource","desc":"Why useful"}}]
}}
Task types: reading, video, practice, quiz, review, project, ai_session"""

class StudyPlanAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY","")
        self.model   = os.getenv("GEMINI_MODEL","gemini-1.5-flash")
        self.can_ai  = bool(self.api_key and not self.api_key.startswith("your_") and GENAI_OK)
        if self.can_ai: genai.configure(api_key=self.api_key)

    def generate_plan(self, subject, goal, deadline, hours_per_day, current_level, user_context):
        if self.can_ai:
            try:
                m = genai.GenerativeModel(self.model, generation_config=genai.types.GenerationConfig(temperature=0.4,max_output_tokens=4000))
                resp = m.generate_content(PLAN_PROMPT.format(subject=subject,goal=goal or f"Master {subject}",deadline=deadline or "4 weeks",hours=hours_per_day,level=current_level,grade=user_context.get("grade","High School"),style=user_context.get("style","visual")))
                text = resp.text.strip()
                text = re.sub(r'^```(?:json)?\s*','',text); text = re.sub(r'\s*```$','',text)
                return json.loads(text)
            except Exception as e:
                print(f"StudyPlan error: {e}")
        return self._fallback(subject, goal, deadline, hours_per_day, current_level)

    def _fallback(self, subject, goal, deadline, hours, level):
        h=int(hours); t=h*30
        return {"title":f"{subject} Mastery Plan","subject":subject,"goal":goal or f"Master {subject}",
                "overview":f"A {h}h/day structured plan to achieve your {subject} goal. Progressing from foundation to mastery in 4 weeks.",
                "total_weeks":4,"daily_hours":h,
                "weeks":[
                    {"week":1,"theme":f"Foundations of {subject}","objectives":[f"Understand core {subject} concepts","Build study habits"],"days":[
                        {"day":"Monday","focus":"Introduction","tasks":[{"task":f"Read intro to {subject}","duration_mins":t,"type":"reading","description":"Overview chapter","resources":["Textbook Ch.1"]}]},
                        {"day":"Tuesday","focus":"Core concepts","tasks":[{"task":"Video lecture","duration_mins":t,"type":"video","description":"Video walkthrough","resources":["Khan Academy / YouTube"]}]},
                        {"day":"Wednesday","focus":"AI Tutor","tasks":[{"task":"NeuroTutor AI session","duration_mins":t,"type":"ai_session","description":"Ask questions, get explanations","resources":["NeuroTutor Chat"]}]},
                        {"day":"Thursday","focus":"Practice","tasks":[{"task":"Problem set","duration_mins":t,"type":"practice","description":"Applied exercises","resources":["Textbook exercises"]}]},
                        {"day":"Friday","focus":"Review + Quiz","tasks":[{"task":"Take AI Quiz","duration_mins":30,"type":"quiz","description":"Test understanding","resources":["NeuroTutor Quiz"]}]}]},
                    {"week":2,"theme":"Intermediate Concepts","objectives":["Apply concepts","Identify gaps"],"days":[
                        {"day":"Monday","focus":"Advanced topics","tasks":[{"task":"Chapter 2-3","duration_mins":t,"type":"reading","description":"Next chapters","resources":["Textbook"]}]},
                        {"day":"Tuesday","focus":"Worked examples","tasks":[{"task":"Study examples","duration_mins":t,"type":"practice","description":"Guided solutions","resources":["Solution manual"]}]},
                        {"day":"Wednesday","focus":"AI deep-dive","tasks":[{"task":"Deep-dive AI session","duration_mins":t,"type":"ai_session","description":"Explore confusing topics","resources":["NeuroTutor"]}]},
                        {"day":"Thursday","focus":"Past papers","tasks":[{"task":"Past exam questions","duration_mins":t,"type":"practice","description":"Exam-style practice","resources":["Past papers"]}]},
                        {"day":"Friday","focus":"Mock test","tasks":[{"task":"Timed mock test","duration_mins":45,"type":"quiz","description":"Simulated exam","resources":["NeuroTutor Quiz"]}]}]}],
                "milestones":[{"week":1,"title":"Foundation Complete","description":"You know the basics","check":["Can explain core concepts","Scored 60%+ on quiz"]},{"week":4,"title":"Goal Achieved","description":goal or "Topic mastered","check":["Scored 85%+ on quiz","Can teach the topic"]}],
                "study_tips":["Use Pomodoro: 25 min focus + 5 min break","Review notes within 24hrs to boost retention 80%","Connect every concept to a real-world example","Use NeuroTutor Socratic mode for deeper understanding","Teach concepts aloud — if you can explain it, you know it"],
                "resources":[{"type":"ai","name":"NeuroTutor AI","desc":"Your personal AI tutor"},{"type":"video","name":"Khan Academy","desc":"Free video lessons"},{"type":"practice","name":"NeuroTutor Quiz","desc":"Adaptive practice tests"}],"_demo":True}
