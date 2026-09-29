import os
import re
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict
from langfuse.langchain import CallbackHandler

from neo4j_client import run_query
from graphrag_search import search_graph_rag

load_dotenv()


# ============================================================
# STATE
# ============================================================

class GraphState(TypedDict):
    question: str
    conversation_history: list
    project_name: str
    project_exists: bool
    required_skills: list
    retrieval_mode: str
    resolved_person: str | None
    is_ambiguous: bool
    candidate_names: list
    person_neo4j_state: dict | None
    graph_data: list
    available_matches: list
    assigned_matches: list
    skill_gaps: list
    role_matches: list
    assignment_state: list
    graphrag_results: list
    answer: str


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

PRONOUN_PATTERNS = [
    r"\bhe\b", r"\bhim\b", r"\bhis\b",
    r"\bshe\b", r"\bher\b", r"\bhers\b",
    r"\bthey\b", r"\bthem\b", r"\btheir\b", r"\btheirs\b",
    r"\bthis person\b", r"\bthat person\b",
    r"\bthis employee\b", r"\bthat employee\b",
    r"\bthe employee\b", r"\bthis candidate\b", r"\bthat candidate\b"
]


def resolve_person_reference(question: str, conversation_history: list):
    """
    Resolve person references from conversation history using Neo4j ground-truth employee names.
    Returns: { "resolved_person": str | None, "is_ambiguous": bool, "candidate_names": list[str] }
    """
    all_employees = run_query("MATCH (e:Employee) RETURN e.name AS name")
    all_names = [e["name"] for e in all_employees]

    lower_q = question.lower()

    # 1. Direct name match in question
    for name in all_names:
        if re.search(r"\b" + re.escape(name.lower()) + r"\b", lower_q):
            return {"resolved_person": name, "is_ambiguous": False, "candidate_names": []}

    # 2. Pronoun / reference detection
    has_pronoun = any(re.search(pat, lower_q) for pat in PRONOUN_PATTERNS)
    if not has_pronoun:
        return {"resolved_person": None, "is_ambiguous": False, "candidate_names": []}

    # 3. Scan conversation history from newest to oldest for mentioned employee names
    mentioned_names = []
    seen = set()
    for turn in reversed(conversation_history[-6:]):
        content = turn.get("content", "")
        for name in all_names:
            if name not in seen and re.search(r"\b" + re.escape(name.lower()) + r"\b", content.lower()):
                mentioned_names.append(name)
                seen.add(name)

    if not mentioned_names:
        return {"resolved_person": None, "is_ambiguous": False, "candidate_names": []}

    if len(mentioned_names) == 1:
        return {"resolved_person": mentioned_names[0], "is_ambiguous": False, "candidate_names": []}

    # If multiple candidates are in history (e.g. Alice and Priya):
    return {"resolved_person": None, "is_ambiguous": True, "candidate_names": mentioned_names[:3]}


# ============================================================
# NODE 1 — ANALYZE QUESTION
# ============================================================

def analyze_question(state: GraphState):
    question = state["question"]
    conversation_history = state.get("conversation_history", [])[-6:]

    # Reference Resolution
    resolution = resolve_person_reference(question, conversation_history)
    resolved_person = resolution["resolved_person"]
    is_ambiguous = resolution["is_ambiguous"]
    candidate_names = resolution["candidate_names"]

    projects = run_query("""
        MATCH (p:Project)
        RETURN p.name AS project_name
        ORDER BY p.name
    """)

    project_names = [project["project_name"] for project in projects]

    prompt = f"""
You are analyzing a workforce management question.

User question:
{question}

Conversation history:
{conversation_history}

Existing projects in the Neo4j database:
{project_names}

Your task:

1. Determine whether the user is asking about or discussing one of the existing projects.
2. If it is an existing project, return that exact project name.
3. If it is NOT an existing project, identify any new project or technical domain discussed, and infer 3 to 5 crucial technical skills for it (e.g., RAG, LangGraph, Python, FastAPI, Neo4j, PyTorch, etc.).

Return EXACTLY this format:

STATUS: EXISTING
PROJECT: exact project name
SKILLS:
RETRIEVAL: STRUCTURED, SEMANTIC, or BOTH

OR

STATUS: NEW
PROJECT: short project name
SKILLS: skill1, skill2, skill3, skill4
RETRIEVAL: STRUCTURED, SEMANTIC, or BOTH
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    status = "NEW"
    project_name = "New Project"
    required_skills = []
    retrieval_mode = "BOTH"

    for line in lines:
        if line.upper().startswith("STATUS:"):
            status_value = line.split(":", 1)[1].strip().upper()
            if status_value == "EXISTING":
                status = "EXISTING"
            else:
                status = "NEW"

        elif line.upper().startswith("PROJECT:"):
            project_name = line.split(":", 1)[1].strip()

        elif line.upper().startswith("SKILLS:"):
            skills_text = line.split(":", 1)[1].strip()
            if skills_text:
                required_skills = [
                    skill.strip()
                    for skill in skills_text.split(",")
                    if skill.strip()
                ]

        elif line.upper().startswith("RETRIEVAL:"):
            candidate_mode = line.split(":", 1)[1].strip().upper()
            if candidate_mode in {"STRUCTURED", "SEMANTIC", "BOTH"}:
                retrieval_mode = candidate_mode

    if status == "EXISTING" and project_name not in project_names:
        status = "NEW"

    # Infer explicit skills from question if required_skills is empty
    if not required_skills:
        for s in ["RAG", "LangGraph", "Python", "FastAPI", "Neo4j", "PyTorch", "PostgreSQL", "Docker", "Cybersecurity"]:
            if re.search(r"\b" + re.escape(s.lower()) + r"\b", question.lower()):
                required_skills.append(s)

    if any(term in question.lower() for term in (
        "recommend", "assign", "available", "staff", "who should", "candidate", "match"
    )):
        retrieval_mode = "BOTH"

    return {
        "project_name": project_name,
        "project_exists": status == "EXISTING",
        "required_skills": required_skills,
        "retrieval_mode": retrieval_mode,
        "resolved_person": resolved_person,
        "is_ambiguous": is_ambiguous,
        "candidate_names": candidate_names,
    }


# ============================================================
# NODE 2 — RETRIEVE FROM NEO4J
# ============================================================

def retrieve_graph_data(state: GraphState):
    if state.get("is_ambiguous"):
        return {
            "graph_data": [],
            "available_matches": [],
            "assigned_matches": [],
            "person_neo4j_state": None,
            "skill_gaps": [],
            "role_matches": [],
            "assignment_state": [],
        }

    # 1. Authoritative assignment state for ALL employees in Neo4j
    assignment_state = run_query("""
        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)
        RETURN e.name AS employee, e.role AS role, p.name AS current_project,
               CASE WHEN p IS NULL THEN "Available" ELSE "Assigned" END AS status
        ORDER BY e.name
    """)

    # 2. Live Neo4j query for specific resolved person
    resolved_person = state.get("resolved_person")
    person_neo4j_state = None
    if resolved_person:
        person_res = run_query("""
            MATCH (e:Employee)
            WHERE toLower(e.name) = toLower($resolved_person)
            OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)
            OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
            RETURN
                e.name AS employee,
                e.role AS role,
                e.department AS department,
                e.experience AS experience,
                p.name AS current_project,
                CASE WHEN p IS NULL THEN "Available" ELSE "Assigned" END AS status,
                collect(DISTINCT s.name) AS skills
        """, {"resolved_person": resolved_person})
        if person_res:
            person_neo4j_state = person_res[0]

    # 3. Determine required skills
    project_name = state["project_name"]
    project_exists = state["project_exists"]
    required_skills = list(state.get("required_skills", []))

    if project_exists:
        existing_skills_res = run_query("""
            MATCH (p:Project {name: $project_name})-[:REQUIRES]->(s:Skill)
            RETURN collect(DISTINCT s.name) AS skills
        """, {"project_name": project_name})
        if existing_skills_res and existing_skills_res[0]["skills"]:
            required_skills = existing_skills_res[0]["skills"]

    # 4. Query ALL employees in Neo4j (DO NOT EXCLUDE ASSIGNED EMPLOYEES)
    if required_skills:
        master_match_query = """
        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(assigned:Project)
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)

        WITH e, assigned, collect(DISTINCT s.name) AS employee_skills

        WITH e, assigned, employee_skills,
             [skill IN $required_skills
              WHERE toLower(skill) IN [sk IN employee_skills | toLower(sk)]] AS matching_skills

        RETURN
            e.name AS employee,
            e.role AS role,
            assigned.name AS current_project,
            CASE WHEN assigned IS NULL THEN "Available" ELSE "Assigned" END AS status,
            employee_skills,
            matching_skills,
            size(matching_skills) AS matching_count,
            size($required_skills) AS total_required,
            CASE
                WHEN size($required_skills) = 0 THEN 0
                ELSE round(100.0 * size(matching_skills) / size($required_skills))
            END AS match_percentage

        ORDER BY match_percentage DESC, status ASC, e.name ASC
        """
        all_candidates = run_query(master_match_query, {"required_skills": required_skills})
    else:
        all_candidates = []

    available_matches = [c for c in all_candidates if c["status"] == "Available" and c["matching_count"] > 0]
    assigned_matches = [c for c in all_candidates if c["status"] == "Assigned" and c["matching_count"] > 0]

    # 5. Skill Gap Analysis
    if project_exists:
        skill_gap_query = """
        MATCH (p:Project {name: $project_name})-[:REQUIRES]->(s:Skill)
        OPTIONAL MATCH (e:Employee)-[:HAS_SKILL]->(s)
        WITH s, count(DISTINCT e) AS employee_count
        RETURN s.name AS skill, employee_count,
               CASE WHEN employee_count = 0 THEN "Missing"
                    WHEN employee_count <= 2 THEN "Scarce"
                    ELSE "Available" END AS status
        ORDER BY employee_count ASC, skill
        """
        skill_gaps = run_query(skill_gap_query, {"project_name": project_name})
    elif required_skills:
        skill_gap_query = """
        UNWIND $required_skills AS required_skill
        OPTIONAL MATCH (s:Skill) WHERE toLower(s.name) = toLower(required_skill)
        OPTIONAL MATCH (e:Employee)-[:HAS_SKILL]->(s)
        WITH required_skill, count(DISTINCT e) AS employee_count
        RETURN required_skill AS skill, employee_count,
               CASE WHEN employee_count = 0 THEN "Missing"
                    WHEN employee_count <= 2 THEN "Scarce"
                    ELSE "Available" END AS status
        ORDER BY employee_count ASC, skill
        """
        skill_gaps = run_query(skill_gap_query, {"required_skills": required_skills})
    else:
        skill_gaps = []

    return {
        "required_skills": required_skills,
        "graph_data": all_candidates[:10],
        "available_matches": available_matches,
        "assigned_matches": assigned_matches,
        "person_neo4j_state": person_neo4j_state,
        "skill_gaps": skill_gaps,
        "role_matches": [],
        "assignment_state": assignment_state,
    }


# ============================================================
# NODE 3 — RETRIEVE SEMANTIC GRAPH RAG CONTEXT
# ============================================================

def retrieve_graphrag_context(state: GraphState):
    if state.get("is_ambiguous"):
        return {"graphrag_results": []}

    if state["retrieval_mode"] == "STRUCTURED":
        return {"graphrag_results": []}

    history = state.get("conversation_history", [])[-4:]
    history_text = "\n".join(
        f"{turn.get('role', 'user')}: {turn.get('content', '')}"
        for turn in history
    )
    semantic_question = f"{history_text}\nLatest question: {state['question']}".strip()
    return {
        "graphrag_results": search_graph_rag(semantic_question, top_k=5)
    }


# ============================================================
# NODE 4 — GENERATE A UNIFIED ANSWER
# ============================================================

def generate_answer(state: GraphState):
    if state.get("is_ambiguous") and state.get("candidate_names"):
        candidates = state["candidate_names"]
        if len(candidates) == 2:
            return {"answer": f"Do you mean {candidates[0]} or {candidates[1]}?"}
        else:
            cand_str = ", ".join(candidates[:-1]) + f", or {candidates[-1]}"
            return {"answer": f"Do you mean {cand_str}?"}

    prompt = f"""
You are WorkGraph AI, a workforce intelligence assistant.

Conversation history:
{state.get('conversation_history', [])[-6:]}

User question:
{state['question']}

Structured Neo4j Context (AUTHORITATIVE GRAPH GROUND TRUTH):
Project: {state.get('project_name')}
Project Exists in Neo4j: {state.get('project_exists')}
Focus Skills: {state.get('required_skills')}
Resolved Specific Person: {state.get('resolved_person')}
Resolved Person Neo4j Status: {state.get('person_neo4j_state')}

Candidate Skill Matches (Calculated across ALL employees in Neo4j):
All Ranked Candidates: {state.get('graph_data')}
Available Candidates with Skill Matches: {state.get('available_matches')}
Assigned Candidates with Skill Matches: {state.get('assigned_matches')}

Organization Skill Gaps: {state.get('skill_gaps')}
Full Neo4j Employee Assignment Roster: {state.get('assignment_state')}

GraphRAG Semantic Document Evidence:
{state.get('graphrag_results')}

CRITICAL DISAMBIGUATION & ACCURACY RULES:
1. MATCHING ≠ AVAILABLE ≠ ASSIGNED:
   - MATCHING means an employee has required skills.
   - AVAILABLE means the employee has NO current assignment in Neo4j (current_project is null).
   - ASSIGNED means the employee is currently committed to a project in Neo4j (current_project is NOT null).
   - NEVER say "No employees have the required skills" or "No matching employees exist" if matching employees exist but are assigned to other projects!

2. RECOMMENDATIONS & CANDIDATE BREAKDOWN:
   When recommending employees or answering "Who should work on X?":
   - Categorize candidates clearly:
     a) Strongest Skill Matches (specify match %, skills matched, AND state their current project if Assigned or state Available).
     b) Currently Available Candidates.
     c) Currently Assigned Candidates.
     d) Skill Gaps (missing/scarce skills).
   - If top skill matches are assigned to other projects, explicitly state:
     "The strongest skill matches are [Names], but they are currently assigned to [Projects]. Currently available candidates are [Names]."

3. SPECIFIC PERSON INQUIRIES & PRONOUN RESOLUTION:
   - If a specific person ({state.get('resolved_person')}) was resolved, answer specifically about that person using their live Neo4j status in `person_neo4j_state`.
   - If they are assigned to a project, explicitly state their current assignment (e.g. "Alice is a 100% skill match, but she is currently assigned to Cloud Migration.").

4. GROUND TRUTH:
   - Base availability ONLY on Neo4j `current_project` / `status` from context. Do not invent assignments or assume someone is available if Neo4j shows them assigned.
   - Keep answer concise, factual, structured, and helpful.
"""
    return {"answer": llm.invoke(prompt).content}


# ============================================================
# LANGGRAPH WORKFLOW
# ============================================================

workflow = StateGraph(GraphState)

workflow.add_node("analyze_question", analyze_question)
workflow.add_node("retrieve_graph_data", retrieve_graph_data)
workflow.add_node("retrieve_graphrag_context", retrieve_graphrag_context)
workflow.add_node("generate_answer", generate_answer)

workflow.add_edge(START, "analyze_question")
workflow.add_edge("analyze_question", "retrieve_graph_data")
workflow.add_edge("retrieve_graph_data", "retrieve_graphrag_context")
workflow.add_edge("retrieve_graphrag_context", "generate_answer")
workflow.add_edge("generate_answer", END)

app = workflow.compile()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    langfuse_handler = CallbackHandler()

    result = app.invoke(
        {
            "question": "Plan an e-commerce recommendation system and suggest who should work on it.",
            "conversation_history": [],
        },
        config={
            "callbacks": [langfuse_handler]
        }
    )

    print("\nAI ANSWER:\n")
    print(result["answer"])
