"""
NeuroTutor AI — Multi-Agent Tutoring System (Google Gemini Edition)
LangGraph 5-node pipeline + Direct Gemini SDK fallback
"""

import os
import json
from typing import TypedDict, List, Optional

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langgraph.graph import StateGraph, END
    LANGCHAIN_OK = True
except ImportError:
    LANGCHAIN_OK = False

try:
    import google.generativeai as genai
    GENAI_OK = True
except ImportError:
    GENAI_OK = False


class AgentState(TypedDict):
    user_message: str; history: List[dict]; user_context: dict
    mode: str; subject: str; intent: str; complexity: str
    knowledge_context: str; curriculum_hints: List[str]
    agent_steps: List[str]; resources: List[dict]
    response: str; follow_up_questions: List[str]
    concept_map: Optional[dict]; error: Optional[str]
    rag_context: Optional[str]; use_pdf: Optional[bool]


BASE_SYSTEM = """You are NeuroTutor — an expert AI tutor that personalizes every explanation.

STUDENT PROFILE:
  Name: {name} | Grade: {grade_level} | Style: {learning_style}
  Subjects: {subjects} | XP Level: {level}

TEACHING RULES:
1. Match language EXACTLY to grade level
2. Visual learners: use tables, ASCII diagrams, structured lists
3. Auditory learners: use narrative flow, storytelling
4. Kinesthetic learners: step-by-step, hands-on examples
5. Reading/Writing: detailed prose with annotations
6. Always connect to real-world applications
7. Be encouraging and positive

CURRENT MODE: {mode}
{mode_instructions}

SUBJECT: {subject}

FORMAT: Use markdown (bold, italic, headers, code blocks, tables).
End with a follow-up question. Suggest 1-2 next topics."""

MODE_INSTRUCTIONS = {
    "tutor": "📖 TUTOR: Comprehensive explanation → worked example → Quick Check question",
    "socratic": "🤔 SOCRATIC: Ask guiding questions only. NEVER give direct answers. Guide discovery.",
    "exam_prep": "📋 EXAM PREP: Key concept → Mnemonics → Common mistakes → Practice question",
    "creative": "🎨 CREATIVE: Use stories, metaphors, analogies. Make it imaginative and fun.",
    "debug": "🔧 DEBUG: [Problem] → [Root cause] → [Step-by-step fix] → [Key lesson]",
}

RESOURCES_DB = {
    "Mathematics":      [{"type":"tool","name":"Wolfram Alpha","url":"https://wolframalpha.com","desc":"Compute math"},{"type":"video","name":"Khan Academy","url":"https://khanacademy.org/math","desc":"Free courses"}],
    "Physics":          [{"type":"sim","name":"PhET Simulations","url":"https://phet.colorado.edu","desc":"Interactive sims"},{"type":"ref","name":"HyperPhysics","url":"http://hyperphysics.phy-astr.gsu.edu","desc":"Physics reference"}],
    "Chemistry":        [{"type":"tool","name":"PubChem","url":"https://pubchem.ncbi.nlm.nih.gov","desc":"Chemical database"},{"type":"learn","name":"ChemLibreTexts","url":"https://chem.libretexts.org","desc":"Free textbooks"}],
    "Computer Science": [{"type":"practice","name":"LeetCode","url":"https://leetcode.com","desc":"Coding problems"},{"type":"learn","name":"CS50","url":"https://cs50.harvard.edu","desc":"Free CS course"}],
    "Biology":          [{"type":"visual","name":"BioDigital","url":"https://www.biodigital.com","desc":"3D anatomy"},{"type":"video","name":"Khan Bio","url":"https://khanacademy.org/science/biology","desc":"Biology courses"}],
}


class TutorAgentGraph:
    def __init__(self, llm):
        self.llm = llm
        wf = StateGraph(AgentState)
        wf.add_node("classify",  self._classify)
        wf.add_node("retrieve",  self._retrieve)
        wf.add_node("map",       self._map)
        wf.add_node("generate",  self._generate)
        wf.add_node("check",     self._check)
        wf.set_entry_point("classify")
        wf.add_edge("classify","retrieve"); wf.add_edge("retrieve","map")
        wf.add_edge("map","generate"); wf.add_edge("generate","check")
        wf.add_edge("check", END)
        self.graph = wf.compile()

    def _classify(self, s):
        msg = s["user_message"].lower(); steps = s.get("agent_steps",[])
        rules = [
            (["explain","what is","what are","define","describe"], "explain_concept"),
            (["solve","calculate","find","compute","how do i"],    "solve_problem"),
            (["example","show me","demonstrate","give me"],        "request_example"),
            (["quiz","test","practice","challenge"],               "request_practice"),
            (["compare","difference","vs","versus","contrast"],    "compare"),
            (["code","program","debug","error","function"],        "code_help"),
        ]
        intent = next((i for kws,i in rules if any(k in msg for k in kws)), "general_question")
        level = s["user_context"].get("level",1)
        complexity = "basic" if level<3 else ("intermediate" if level<7 else "advanced")
        steps.append(f"🔍 Intent: **{intent.replace('_',' ').title()}** | Complexity: **{complexity}**")
        return {**s,"intent":intent,"complexity":complexity,"agent_steps":steps}

    def _retrieve(self, s):
        steps = s["agent_steps"]
        subj = s["subject"]
        ctx = {"explain_concept":f"Clear conceptual explanation with real-world connections in {subj}.",
               "solve_problem":  f"Systematic step-by-step problem solving in {subj}.",
               "request_example":f"Concrete relatable examples from {subj}.",
               "request_practice":f"Practice material at student's level in {subj}.",
               "compare":        f"Similarities, differences, trade-offs in {subj}.",
               "code_help":      f"Clear debugging and programming explanation in {subj}.",
               "general_question":f"Comprehensive helpful answer about {subj}."}.get(s["intent"], f"Answer about {subj}.")
        resources = RESOURCES_DB.get(subj, [{"type":"ref","name":"Khan Academy","url":"https://khanacademy.org","desc":"Free learning"}])[:2]
        steps.append(f"📚 Knowledge retrieved for **{subj}**")
        return {**s,"knowledge_context":ctx,"resources":resources,"agent_steps":steps}

    def _map(self, s):
        steps = s["agent_steps"]
        steps.append(f"🗺️ Curriculum pathway mapped")
        return {**s,"agent_steps":steps}

    def _generate(self, s):
        steps = s["agent_steps"]; ctx = s["user_context"]; mode = s.get("mode","tutor")
        rag = s.get("rag_context") or ""
        rag_block = ""
        if rag:
            rag_block = f"\n\nPDF DOCUMENT CONTEXT (student's uploaded syllabus/textbook):\n---\n{rag}\n---\nGround your answer in the above document. Reference it specifically. Give a clear step-by-step solution."
        sys_p = BASE_SYSTEM.format(
            name=ctx.get("name","Student"), grade_level=ctx.get("grade_level","High School"),
            learning_style=ctx.get("learning_style","visual"),
            subjects=", ".join(ctx.get("subjects",[])) or "General",
            level=ctx.get("level",1), mode=mode.replace("_"," ").title(),
            mode_instructions=MODE_INSTRUCTIONS.get(mode,MODE_INSTRUCTIONS["tutor"]),
            subject=s.get("subject","General")) + rag_block
        msgs = [SystemMessage(content=sys_p)]
        for m in s["history"][-8:]:
            if isinstance(m,dict):
                if m.get("role")=="user": msgs.append(HumanMessage(content=m["content"]))
                elif m.get("role")=="assistant": msgs.append(AIMessage(content=m["content"]))
        user_msg = s['user_message']
        if rag:
            user_msg += f"\n\n[Retrieved from your PDF: {rag[:400]}...]"
        msgs.append(HumanMessage(content=f"{user_msg}\n[Context: {s.get('knowledge_context','')}]"))
        steps.append(f"🤖 Gemini generating **{mode}** response..." + (" 📄 PDF context injected" if rag else ""))
        resp = self.llm.invoke(msgs)
        steps.append("✨ Response complete")
        return {**s,"response":resp.content,"agent_steps":steps}

    def _check(self, s):
        r = s.get("response","")
        if not r or len(r)<20:
            s["response"] = "I couldn't generate a proper response. Please rephrase your question!"
        s["follow_up_questions"] = [l.strip().lstrip("•-* ") for l in r.split("\n") if l.strip().endswith("?") and len(l.strip())>20][:2]
        return s

    def invoke(self, state): return self.graph.invoke(state)


class TutorAgent:
    def __init__(self):
        self.api_key    = os.getenv("GEMINI_API_KEY","")
        self.model_name = os.getenv("GEMINI_MODEL","gemini-1.5-flash")
        self.llm = None; self.graph = None
        self._init()

    def _init(self):
        if not self.api_key or self.api_key.startswith("your_"):
            print("⚠️  No GEMINI_API_KEY — demo mode. Get free key: aistudio.google.com/app/apikey"); return
        if LANGCHAIN_OK:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name, google_api_key=self.api_key,
                    max_output_tokens=int(os.getenv("MAX_TOKENS",4096)),
                    temperature=0.7, convert_system_message_to_human=True)
                self.graph = TutorAgentGraph(self.llm)
                print(f"✅ TutorAgent: LangGraph + Gemini ({self.model_name})"); return
            except Exception as e:
                print(f"⚠️  LangGraph init failed: {e}")
        if GENAI_OK:
            genai.configure(api_key=self.api_key)
            print(f"✅ TutorAgent: Direct Gemini SDK ({self.model_name})")
        else:
            print("⚠️  No AI libraries — demo mode")

    def chat(self, message, history, user_context, mode="tutor", subject="General", rag_context=""):
        state = AgentState(user_message=message, history=history, user_context=user_context,
                           mode=mode, subject=subject, intent="", complexity="intermediate",
                           knowledge_context="", curriculum_hints=[], agent_steps=[],
                           resources=[], response="", follow_up_questions=[], concept_map=None, error=None,
                           rag_context=rag_context or "", use_pdf=bool(rag_context))
        if self.graph:
            try:
                r = self.graph.invoke(state)
                return {"content":r["response"],"agent_steps":r["agent_steps"],"resources":r["resources"],
                        "follow_up_questions":r["follow_up_questions"],"concept_map":None,"mode":mode}
            except Exception as e: print(f"LangGraph error: {e}")
        if self.api_key and not self.api_key.startswith("your_") and GENAI_OK:
            try: return self._direct(message, history, user_context, mode, subject)
            except Exception as e: print(f"Direct Gemini error: {e}")
        return self._demo(message, user_context, mode)

    def _direct(self, message, history, ctx, mode, subject):
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=BASE_SYSTEM.format(
                name=ctx.get("name","Student"), grade_level=ctx.get("grade_level","High School"),
                learning_style=ctx.get("learning_style","visual"),
                subjects=", ".join(ctx.get("subjects",[])) or "General",
                level=ctx.get("level",1), mode=mode.replace("_"," ").title(),
                mode_instructions=MODE_INSTRUCTIONS.get(mode,MODE_INSTRUCTIONS["tutor"]),
                subject=subject),
            generation_config=genai.types.GenerationConfig(max_output_tokens=4096, temperature=0.7))
        hist = [{"role":"user" if m["role"]=="user" else "model","parts":[m["content"]]} for m in history[-8:] if isinstance(m,dict) and m.get("role") in ("user","assistant")]
        chat = model.start_chat(history=hist)
        resp = chat.send_message(message)
        return {"content":resp.text,"agent_steps":["🔍 Classified","📚 Retrieved","🤖 Gemini responded","✨ Done"],
                "resources":[],"follow_up_questions":[],"concept_map":None,"mode":mode}

    def _demo(self, message, ctx, mode):
        name = ctx.get("name","Student")
        return {"content":f"""**Demo Mode — Add Your Gemini API Key, {name}!** 🎓

Your question: *"{message}"*

**Get your FREE Google Gemini API key in 60 seconds:**
1. Visit → **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account (free)
3. Click **"Create API Key"**
4. Copy it into your `.env` file:
   ```
   GEMINI_API_KEY=AIza...your_key_here
   ```
5. Restart: `python app.py`

The free tier gives you **1 million tokens/month** — more than enough!""",
                "agent_steps":["🎭 Demo mode — add GEMINI_API_KEY for full AI"],
                "resources":[{"type":"setup","name":"Get Free Gemini API Key","url":"https://aistudio.google.com/app/apikey","desc":"Free 1M tokens/month"}],
                "follow_up_questions":["Ready to add your free Gemini API key?"],
                "concept_map":None,"mode":mode}

    def explain_concept(self, concept, style, grade):
        return self.chat(f"Explain: {concept}",[],{"name":"Student","grade_level":grade,"learning_style":style,"subjects":[],"level":1})
