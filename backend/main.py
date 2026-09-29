from fastapi import FastAPI
from pydantic import BaseModel, Field
from threading import RLock
from uuid import uuid4
from neo4j_client import run_query
from ai_workflow import app as ai_workflow
from graphrag_search import search_graph_rag
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

app = FastAPI(title="WorkGraph AI")

# Demo-scale, process-local conversation memory. Neo4j remains the source of
# truth for workforce state because every workflow run queries it again.
conversation_store: dict[str, list[dict[str, str]]] = {}
conversation_lock = RLock()
MAX_CONVERSATION_MESSAGES = 12


class ConversationTurn(BaseModel):
    role: str
    content: str


class AssistantRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    # Kept for clients using the previous unified endpoint contract. New
    # clients should use conversation_id and let this process retain history.
    history: list[ConversationTurn] = Field(default_factory=list, max_length=12)


@app.get("/")
def home():
    return {"message": "WorkGraph AI API is running"}


@app.get("/employees")
def get_employees():
    return run_query("""
        MATCH (e:Employee)
        RETURN
            e.id AS id,
            e.name AS name,
            e.role AS role,
            e.department AS department,
            e.experience AS experience
        ORDER BY e.name
    """)


@app.get("/projects")
def get_projects():
    return run_query("""
        MATCH (p:Project)
        RETURN
            p.id AS id,
            p.name AS name,
            p.status AS status
        ORDER BY p.name
    """)

@app.get("/projects/{project_name}/match")
def match_employees(project_name: str):
    return run_query("""
        MATCH (p:Project {name: $project_name})-[:REQUIRES]->(required:Skill)
        WITH p, count(required) AS total_required

        MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill)
        WHERE (p)-[:REQUIRES]->(s)
          AND NOT (e)-[:ASSIGNED_TO]->()

        WITH e, total_required, count(s) AS matching_skills

        RETURN
            e.name AS employee,
            e.role AS role,
            matching_skills,
            total_required,
            round(
                100.0 * matching_skills / total_required
            ) AS match_percentage

        ORDER BY match_percentage DESC
    """, {"project_name": project_name})

@app.get("/projects/{project_name}/skill-gaps")
def get_skill_gaps(project_name: str):
    return run_query("""
        MATCH (p:Project {name: $project_name})-[:REQUIRES]->(s:Skill)
        OPTIONAL MATCH (e:Employee)-[:HAS_SKILL]->(s)

        WITH s, count(DISTINCT e) AS employee_count

        RETURN
            s.name AS skill,
            employee_count,
            CASE
                WHEN employee_count = 0 THEN "Missing"
                WHEN employee_count <= 2 THEN "Scarce"
                ELSE "Available"
            END AS status

        ORDER BY employee_count ASC, skill
    """, {"project_name": project_name})

@app.get("/ai/ask")
def ask_ai(question: str):
    result = ai_workflow.invoke({
        "question": question,
        "conversation_history": []
    })

    return {
        "question": question,
        "answer": result["answer"]
    }


@app.post("/ai/assistant")
def ask_unified_assistant(request: AssistantRequest):
    """Run one turn in an in-memory, session/thread-scoped conversation."""
    conversation_id = request.conversation_id or str(uuid4())

    with conversation_lock:
        if conversation_id not in conversation_store:
            conversation_store[conversation_id] = [
                turn.dict() for turn in request.history[-MAX_CONVERSATION_MESSAGES:]
            ]
        history = list(conversation_store[conversation_id])

    result = ai_workflow.invoke({
        "question": request.question,
        "conversation_history": history,
    })

    with conversation_lock:
        messages = conversation_store.setdefault(conversation_id, history)
        messages.extend([
            {"role": "user", "content": request.question},
            {"role": "assistant", "content": result["answer"]},
        ])
        del messages[:-MAX_CONVERSATION_MESSAGES]

    return {
        "conversation_id": conversation_id,
        "question": request.question,
        "answer": result["answer"],
        "retrieval_mode": result["retrieval_mode"],
        "graphrag_results": result["graphrag_results"],
    }

@app.get("/employees/availability")
def get_employee_availability():
    return run_query("""
        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)

        RETURN
            e.name AS employee,
            e.role AS role,
            CASE
                WHEN p IS NULL THEN "Available"
                ELSE "Assigned"
            END AS status,
            p.name AS current_project
        ORDER BY e.name
    """)

@app.get("/employees/{employee_name}/assignment")
def get_employee_assignment(employee_name: str):
    return run_query("""
        MATCH (e:Employee {name: $employee_name})
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)

        RETURN
            e.name AS employee,
            CASE
                WHEN p IS NULL THEN "Available"
                ELSE "Assigned"
            END AS status,
            p.name AS current_project
    """, {"employee_name": employee_name})

@app.post("/employees/{employee_name}/assign/{project_name}")
def assign_employee(employee_name: str, project_name: str):

    existing = run_query("""
        MATCH (e:Employee {name: $employee_name})
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)

        RETURN p.name AS current_project
    """, {"employee_name": employee_name})

    if existing and existing[0]["current_project"]:
        return {
            "success": False,
            "message": f"{employee_name} is already assigned to "
                       f"{existing[0]['current_project']}"
        }

    result = run_query("""
        MATCH (e:Employee {name: $employee_name})
        MATCH (p:Project {name: $project_name})

        MERGE (e)-[:ASSIGNED_TO]->(p)

        RETURN e.name AS employee, p.name AS project
    """, {
        "employee_name": employee_name,
        "project_name": project_name
    })

    if not result:
        return {
            "success": False,
            "message": "Employee or project not found"
        }

    return {
        "success": True,
        "message": f"{employee_name} assigned to {project_name}"
    }

@app.post("/employees/{employee_name}/unassign")
def unassign_employee(employee_name: str):

    result = run_query("""
        MATCH (e:Employee {name: $employee_name})
        OPTIONAL MATCH (e)-[r:ASSIGNED_TO]->(p:Project)

        WITH e, r, p
        DELETE r

        RETURN
            e.name AS employee,
            p.name AS previous_project
    """, {"employee_name": employee_name})

    if not result:
        return {
            "success": False,
            "message": "Employee not found"
        }

    return {
        "success": True,
        "message": f"{employee_name} is now available",
        "previous_project": result[0]["previous_project"]
    }

@app.get("/graphrag/search")
def graph_rag_search(question: str, top_k: int = 5):
    results = search_graph_rag(question, top_k=top_k)

    return {
        "question": question,
        "results": results
    }

@app.get("/graphrag/recommend/{project_name}")
def graphrag_recommend(project_name: str, top_k: int = 5):

    # Step 1: Get project requirements from the graph
    project_data = run_query("""
        MATCH (p:Project)
        WHERE toLower(p.name) = toLower($project_name)

        OPTIONAL MATCH (p)-[:REQUIRES]->(s:Skill)

        RETURN
            p.name AS project,
            collect(DISTINCT s.name) AS required_skills
    """, {"project_name": project_name})

    if not project_data:
        return {
            "success": False,
            "message": f"Project '{project_name}' not found"
        }

    project = project_data[0]

    required_skills = project["required_skills"]

    # Step 2: Find available employees and compare skills
    recommendations = run_query("""
        MATCH (p:Project)
        WHERE toLower(p.name) = toLower($project_name)

        MATCH (e:Employee)

        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(assigned:Project)

        WHERE assigned IS NULL

        OPTIONAL MATCH (e)-[:HAS_SKILL]->(skill:Skill)

        WITH
            p,
            e,
            collect(DISTINCT skill.name) AS employee_skills

        WITH
            p,
            e,
            employee_skills,
            [skill IN employee_skills
             WHERE skill IN $required_skills] AS matching_skills

        RETURN
            e.name AS employee,
            e.role AS role,
            employee_skills,
            matching_skills,
            [skill IN $required_skills
             WHERE NOT skill IN employee_skills] AS missing_skills,

            CASE
                WHEN size($required_skills) = 0 THEN 0
                ELSE round(
                    100.0 * size(matching_skills)
                    / size($required_skills)
                )
            END AS match_percentage

        ORDER BY match_percentage DESC
    """, {
        "project_name": project_name,
        "required_skills": required_skills
    })

    # Step 3: Retrieve relevant unstructured knowledge
    question = (
        f"Who has experience relevant to the project "
        f"{project['project']} requiring "
        f"{', '.join(required_skills)}?"
    )

    semantic_results = search_graph_rag(question, top_k)

    # Step 4: Combine graph + vector results
    semantic_by_employee = {}

    for result in semantic_results:
        if "Employee" in result["entity_type"]:
            semantic_by_employee[result["entity_name"]] = {
                "similarity": result["score"],
                "document": result["document"],
                "relevant_text": result["chunk"],
                "worked_projects": result["worked_projects"]
            }

    final_results = []

    for employee in recommendations:

        extra = semantic_by_employee.get(
            employee["employee"],
            {}
        )

        final_results.append({
            **employee,
            "semantic_similarity": extra.get("similarity", 0),
            "document": extra.get("document"),
            "relevant_experience": extra.get("relevant_text"),
            "worked_projects": extra.get("worked_projects", [])
        })

    return {
        "success": True,
        "project": project["project"],
        "required_skills": required_skills,
        "recommendations": final_results
    }

@app.get("/graphrag/ask")
def graph_rag_ask(question: str, top_k: int = 5):

    results = search_graph_rag(question, top_k=top_k)

    context = []

    for result in results:

        context.append(
            f"""
Entity: {result.get('entity_name')}
Type: {result.get('entity_type')}
Role: {result.get('role')}
Department: {result.get('department')}

Employee Skills:
{result.get('employee_skills')}

Worked Projects:
{result.get('worked_projects')}

Assigned Projects:
{result.get('assigned_projects')}

Relevant Document:
{result.get('chunk')}
"""
        )

    graph_context = "\n\n".join(context)

    prompt = f"""
You are a workforce intelligence assistant.

Answer the user's question using ONLY the information
provided in the GraphRAG context below.

User question:
{question}

GraphRAG context:
{graph_context}

Rules:
- Do not invent employees, skills, projects, or experience.
- Distinguish between direct experience and general similarity.
- If an employee's document says they have limited experience,
  mention that limitation.
- Use the employee's skills and project history as supporting
  evidence.
- Keep the answer concise and factual.
- If the retrieved information is insufficient, say so.

Give a clear answer to the user's question.
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "answer": response.content,
        "results": results
    }
