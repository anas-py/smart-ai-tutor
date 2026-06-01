"""Quiz Agent — AI quiz generation using Google Gemini"""
import os, json, re

try:
    import google.generativeai as genai
    GENAI_OK = True
except ImportError:
    GENAI_OK = False

QUIZ_PROMPT = """Generate a {num_q}-question multiple-choice quiz on "{topic}" in {subject}.
Difficulty: {difficulty}. Student level: {level}/10.

Return ONLY valid JSON, no markdown fences, no extra text:
{{
  "title": "Engaging quiz title",
  "subject": "{subject}",
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "estimated_mins": {mins},
  "questions": [
    {{
      "id": 1,
      "type": "mcq",
      "question": "Clear question text?",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct": "A",
      "explanation": "Educational explanation of why A is correct",
      "hint": "Helpful hint without giving away the answer",
      "points": 10,
      "tags": ["topic_tag"]
    }}
  ]
}}
Rules: One clearly correct answer. Distractors plausible but wrong. Explanations teach. Mix recall/application/analysis. Points: easy=5, medium=10, hard=15."""

FALLBACK = {
    "Mathematics": {"title":"Mathematics Challenge","questions":[
        {"id":1,"type":"mcq","question":"What is the derivative of sin(x)?","options":{"A":"cos(x)","B":"-cos(x)","C":"-sin(x)","D":"tan(x)"},"correct":"A","explanation":"d/dx[sin(x)] = cos(x) — a fundamental calculus identity.","hint":"Think about rates of change on the unit circle.","points":10,"tags":["calculus"]},
        {"id":2,"type":"mcq","question":"Solve 2x² - 8 = 0. What is x?","options":{"A":"±2","B":"±4","C":"±√8","D":"4"},"correct":"A","explanation":"2x²=8 → x²=4 → x=±2. Always check both roots.","hint":"Isolate x² first, then square root.","points":10,"tags":["algebra"]},
        {"id":3,"type":"mcq","question":"log₂(64) = ?","options":{"A":"4","B":"6","C":"8","D":"32"},"correct":"B","explanation":"log₂(64)=6 because 2⁶=64.","hint":"Ask: 2 to what power = 64?","points":10,"tags":["logarithms"]},
        {"id":4,"type":"mcq","question":"Sum of interior angles of a hexagon?","options":{"A":"540°","B":"620°","C":"720°","D":"900°"},"correct":"C","explanation":"(n-2)×180° = (6-2)×180 = 720°","hint":"Formula: (n-2)×180°","points":10,"tags":["geometry"]},
        {"id":5,"type":"mcq","question":"P(rolling 6 on fair die)?","options":{"A":"1/3","B":"1/6","C":"1/4","D":"1/2"},"correct":"B","explanation":"6 equally likely outcomes, 1 is a six = 1/6.","hint":"Favorable ÷ Total","points":5,"tags":["probability"]}]},
    "Physics": {"title":"Physics Explorer","questions":[
        {"id":1,"type":"mcq","question":"F = ma is Newton's ___ Law?","options":{"A":"First","B":"Second","C":"Third","D":"Fourth"},"correct":"B","explanation":"Newton's Second Law: Force = mass × acceleration.","hint":"This law relates force to motion change.","points":10,"tags":["mechanics"]},
        {"id":2,"type":"mcq","question":"Unit of electric resistance?","options":{"A":"Ampere","B":"Volt","C":"Ohm","D":"Watt"},"correct":"C","explanation":"Resistance is in Ohms (Ω), named after Georg Ohm.","hint":"V=IR — what's R measured in?","points":5,"tags":["electricity"]},
        {"id":3,"type":"mcq","question":"Which wave needs a medium?","options":{"A":"Light","B":"Radio","C":"Sound","D":"Gamma"},"correct":"C","explanation":"Sound is mechanical — needs particles to transfer energy.","hint":"Can sound travel in a vacuum?","points":10,"tags":["waves"]},
        {"id":4,"type":"mcq","question":"Speed of light in vacuum ≈?","options":{"A":"3×10⁶ m/s","B":"3×10⁸ m/s","C":"3×10¹⁰ m/s","D":"3×10⁴ m/s"},"correct":"B","explanation":"c ≈ 3×10⁸ m/s — a fundamental physical constant.","hint":"c = 3×10? m/s","points":15,"tags":["light"]},
        {"id":5,"type":"mcq","question":"Why is the sky blue?","options":{"A":"Reflection","B":"Refraction","C":"Rayleigh scattering","D":"Diffraction"},"correct":"C","explanation":"Blue light (short wavelength) scatters more = blue sky.","hint":"Shorter wavelengths scatter more.","points":15,"tags":["optics"]}]},
    "Computer Science": {"title":"CS Challenge","questions":[
        {"id":1,"type":"mcq","question":"Time complexity of binary search?","options":{"A":"O(n)","B":"O(n²)","C":"O(log n)","D":"O(1)"},"correct":"C","explanation":"Binary search halves the search space each step: O(log n).","hint":"How many times can you halve n before reaching 1?","points":15,"tags":["algorithms"]},
        {"id":2,"type":"mcq","question":"LIFO data structure?","options":{"A":"Queue","B":"Stack","C":"Linked List","D":"Tree"},"correct":"B","explanation":"Stack = Last In, First Out. Like a pile of plates.","hint":"Think of a pile of plates.","points":10,"tags":["data structures"]},
        {"id":3,"type":"mcq","question":"SQL stands for?","options":{"A":"Structured Query Language","B":"Simple Question Language","C":"System Query Logic","D":"Sequential Queue Language"},"correct":"A","explanation":"SQL = Structured Query Language for databases.","hint":"Used for databases.","points":5,"tags":["databases"]},
        {"id":4,"type":"mcq","question":"Best average-case sort complexity?","options":{"A":"Bubble Sort O(n²)","B":"Selection Sort O(n²)","C":"Merge Sort O(n log n)","D":"Insertion Sort O(n²)"},"correct":"C","explanation":"Merge Sort O(n log n) best average and worst case.","hint":"Which divide-and-conquer sort is consistently fast?","points":15,"tags":["sorting"]},
        {"id":5,"type":"mcq","question":"type(range(5)) in Python?","options":{"A":"list","B":"tuple","C":"range","D":"generator"},"correct":"C","explanation":"range() returns a range object, not a list.","hint":"Try type(range(5)) in Python shell.","points":10,"tags":["python"]}]},
    "Chemistry": {"title":"Chemistry Quiz","questions":[
        {"id":1,"type":"mcq","question":"Atomic number of Carbon?","options":{"A":"6","B":"12","C":"14","D":"8"},"correct":"A","explanation":"Carbon has 6 protons → atomic number 6.","hint":"Atomic number = protons.","points":5,"tags":["elements"]},
        {"id":2,"type":"mcq","question":"Bond type in NaCl?","options":{"A":"Covalent","B":"Metallic","C":"Ionic","D":"Hydrogen"},"correct":"C","explanation":"Na loses electron to Cl → ionic bond via electrostatic attraction.","hint":"Metal + non-metal → ?","points":10,"tags":["bonding"]},
        {"id":3,"type":"mcq","question":"pH of neutral solution at 25°C?","options":{"A":"0","B":"7","C":"14","D":"1"},"correct":"B","explanation":"pH 7 = neutral (equal H⁺ and OH⁻ ions).","hint":"The pH scale is 0–14. Middle = neutral.","points":5,"tags":["acids-bases"]}]},
    "Biology": {"title":"Biology Quiz","questions":[
        {"id":1,"type":"mcq","question":"Where does photosynthesis occur?","options":{"A":"Mitochondria","B":"Nucleus","C":"Chloroplast","D":"Ribosome"},"correct":"C","explanation":"Chloroplasts contain chlorophyll and are the photosynthesis site.","hint":"Which organelle is green?","points":5,"tags":["cell biology"]},
        {"id":2,"type":"mcq","question":"DNA monomers are called?","options":{"A":"Amino acids","B":"Fatty acids","C":"Nucleotides","D":"Monosaccharides"},"correct":"C","explanation":"DNA is a polynucleotide chain of nucleotide monomers.","hint":"Building blocks of genetic material.","points":10,"tags":["genetics"]},
        {"id":3,"type":"mcq","question":"Powerhouse of the cell?","options":{"A":"Nucleus","B":"Ribosome","C":"Golgi body","D":"Mitochondria"},"correct":"D","explanation":"Mitochondria produce ATP via cellular respiration.","hint":"Which organelle produces ATP?","points":5,"tags":["cell organelles"]}]},
}

class QuizAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY","")
        self.model   = os.getenv("GEMINI_MODEL","gemini-1.5-flash")
        self.can_ai  = bool(self.api_key and not self.api_key.startswith("your_") and GENAI_OK)
        if self.can_ai:
            genai.configure(api_key=self.api_key)

    def generate_quiz(self, subject, topic, difficulty, num_questions, user_level):
        topic = topic or f"Core {subject} Concepts"
        mins  = num_questions * (2 if difficulty=="easy" else 3 if difficulty=="medium" else 4)
        if self.can_ai:
            try:
                return self._ai_gen(subject, topic, difficulty, num_questions, user_level, mins)
            except Exception as e:
                print(f"Quiz AI error: {e}")
        return self._fallback(subject, topic, difficulty, num_questions)

    def _ai_gen(self, subject, topic, difficulty, num_q, level, mins):
        model = genai.GenerativeModel(self.model, generation_config=genai.types.GenerationConfig(temperature=0.3, max_output_tokens=3000))
        resp  = model.generate_content(QUIZ_PROMPT.format(num_q=num_q, topic=topic, subject=subject, difficulty=difficulty, level=level, mins=mins))
        text  = resp.text.strip()
        text  = re.sub(r'^```(?:json)?\s*','',text); text = re.sub(r'\s*```$','',text)
        data  = json.loads(text)
        if "questions" not in data or not data["questions"]: raise ValueError("Invalid quiz structure")
        return data

    def _fallback(self, subject, topic, difficulty, num_questions):
        bank = FALLBACK.get(subject, FALLBACK["Mathematics"])
        qs   = bank["questions"][:num_questions]
        for i,q in enumerate(qs,1): q["id"]=i
        return {"title":bank["title"],"subject":subject,"topic":topic,"difficulty":difficulty,
                "estimated_mins":len(qs)*3,"questions":qs,"_demo":True}

    def evaluate_quiz(self, answers, quiz_data):
        questions = quiz_data.get("questions",[])
        if not questions: return {"score":0,"correct":0,"total":0,"feedback":[],"grade":"F","message":"No questions"}
        correct=0; tp=0; ep=0; feedback=[]
        for q in questions:
            qid=str(q.get("id","")); correct_ans=q.get("correct","").upper()
            user_ans=(answers.get(qid) or "").upper(); is_ok=user_ans==correct_ans
            pts=q.get("points",10); tp+=pts
            if is_ok: correct+=1; ep+=pts
            feedback.append({"question_id":qid,"question":q.get("question",""),"user_answer":user_ans,
                             "correct_answer":correct_ans,"is_correct":is_ok,"explanation":q.get("explanation",""),
                             "points_earned":pts if is_ok else 0,"points_max":pts,"tags":q.get("tags",[])})
        total=len(questions); score=round(correct/total*100,1) if total>0 else 0
        grade="A+"if score==100 else"A"if score>=90 else"B"if score>=80 else"C"if score>=70 else"D"if score>=60 else"F"
        msgs={"A+":"🌟 PERFECT! Complete mastery!","A":"🎉 Excellent!","B":"👏 Great work!","C":"💪 Good effort — review explanations.","D":"📚 Keep practicing!","F":"🔄 Review this topic with your AI tutor!"}
        weak=[t for f in feedback if not f["is_correct"] for t in f.get("tags",[])]
        return {"score":score,"correct":correct,"total":total,"earned_points":ep,"total_points":tp,
                "grade":grade,"message":msgs[grade],"feedback":feedback,"weak_tags":list(dict.fromkeys(weak))[:5]}
