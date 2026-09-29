from neo4j_client import driver


# Requirements taken from the project/role knowledge documents
# and synchronized into the structured Neo4j graph.

PROJECT_REQUIREMENTS = {
    "AI Customer Assistant": [
        "Python",
        "FastAPI",
        "RAG",
        "LangGraph",
        "PostgreSQL",
    ],
    "E-Commerce Recommendation System": [
        "Python",
        "Machine Learning",
        "PostgreSQL",
        "Data Pipelines",
    ],
    "Workforce Graph Intelligence": [
        "Neo4j",
        "Python",
        "LangGraph",
        "RAG",
        "Vector Search",
    ],
    "Internal HR Portal": [
        "React",
        "TypeScript",
        "REST APIs",
        "PostgreSQL",
        "Docker",
    ],
    "Security Monitoring Platform": [
        "Cybersecurity",
        "Python",
        "Linux",
        "SIEM",
    ],
    "Intelligent Travel Planner": [
        "Python",
        "LangGraph",
        "API Integration",
        "PostgreSQL",
    ],
}


ROLE_REQUIREMENTS = {
    "AI Engineer": [
        "Python",
        "RAG",
        "LangGraph",
        "Machine Learning",
        "Vector Search",
    ],
    "Backend Developer": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "REST APIs",
        "Docker",
    ],
    "Frontend Developer": [
        "React",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
    ],
    "Cybersecurity Engineer": [
        "Cybersecurity",
        "Python",
        "Linux",
        "SIEM",
    ],
    "Data Engineer": [
        "Python",
        "SQL",
        "Data Pipelines",
        "PostgreSQL",
    ],
    "DevOps Engineer": [
        "Docker",
        "Linux",
        "CI/CD",
        "Kubernetes",
    ],
}


def sync_requirements():

    with driver.session() as session:

        # --------------------------------------------------
        # PROJECT REQUIREMENTS
        # --------------------------------------------------

        for project_name, skills in PROJECT_REQUIREMENTS.items():

            for skill_name in skills:

                session.run(
                    """
                    MATCH (p:Project {name: $project_name})

                    MERGE (s:Skill {name: $skill_name})

                    MERGE (p)-[:REQUIRES]->(s)
                    """,
                    project_name=project_name,
                    skill_name=skill_name,
                )

        # --------------------------------------------------
        # ROLE REQUIREMENTS
        # --------------------------------------------------

        for role_name, skills in ROLE_REQUIREMENTS.items():

            for skill_name in skills:

                session.run(
                    """
                    MATCH (r:Role {name: $role_name})

                    MERGE (s:Skill {name: $skill_name})

                    MERGE (r)-[:REQUIRES]->(s)
                    """,
                    role_name=role_name,
                    skill_name=skill_name,
                )

    print("Requirement synchronization completed.")


if __name__ == "__main__":
    sync_requirements()