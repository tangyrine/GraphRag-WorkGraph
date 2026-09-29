from sentence_transformers import SentenceTransformer

from neo4j_client import driver


model = SentenceTransformer("all-MiniLM-L6-v2")


def get_graph_context(session, entity_name, entity_type):

    if "Employee" in entity_type:

        result = session.run(
            """
            MATCH (e:Employee {name: $name})

            OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
            WITH e, collect(DISTINCT s.name) AS skills

            OPTIONAL MATCH (e)-[:WORKED_ON]->(p:Project)
            WITH e, skills, collect(DISTINCT p.name) AS worked_on

            OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(ap:Project)

            RETURN
                skills,
                worked_on,
                collect(DISTINCT ap.name) AS assigned_projects
            """,
            name=entity_name,
        )

        record = result.single()

        if not record:
            return {
                "employee_skills": [],
                "worked_projects": [],
                "required_skills": [],
                "tasks": [],
                "assigned_projects": [],
            }

        return {
            "employee_skills": record["skills"],
            "worked_projects": record["worked_on"],
            "required_skills": [],
            "tasks": [],
            "assigned_projects": record["assigned_projects"],
        }

    elif "Project" in entity_type:

        result = session.run(
            """
            MATCH (p:Project)
            WHERE toLower(p.name) = toLower($name)

            OPTIONAL MATCH (p)-[:REQUIRES]->(s:Skill)
            WITH p, collect(DISTINCT s.name) AS required_skills

            OPTIONAL MATCH (p)-[:HAS_TASK]->(t:Task)

            RETURN
                required_skills,
                collect(DISTINCT t.name) AS tasks
            """,
            name=entity_name,
        )

        record = result.single()

        if not record:
            return {
                "employee_skills": [],
                "worked_projects": [],
                "required_skills": [],
                "tasks": [],
                "assigned_projects": [],
            }

        return {
            "employee_skills": [],
            "worked_projects": [],
            "required_skills": record["required_skills"],
            "tasks": record["tasks"],
            "assigned_projects": [],
        }

    elif "Role" in entity_type:

        result = session.run(
            """
            MATCH (r:Role)
            WHERE toLower(r.name) = toLower($name)

            OPTIONAL MATCH (r)-[:REQUIRES]->(s:Skill)

            RETURN collect(DISTINCT s.name) AS required_skills
            """,
            name=entity_name,
        )

        record = result.single()

        if not record:
            return {
                "employee_skills": [],
                "worked_projects": [],
                "required_skills": [],
                "tasks": [],
                "assigned_projects": [],
            }

        return {
            "employee_skills": [],
            "worked_projects": [],
            "required_skills": record["required_skills"],
            "tasks": [],
            "assigned_projects": [],
        }

    return {
        "employee_skills": [],
        "worked_projects": [],
        "required_skills": [],
        "tasks": [],
        "assigned_projects": [],
    }


def search_graph_rag(question: str, top_k: int = 5):

    embedding = model.encode(question).tolist()

    with driver.session() as session:

        vector_result = session.run(
            """
            CALL db.index.vector.queryNodes(
                'chunk_embedding_index',
                $top_k,
                $embedding
            )
            YIELD node, score

            MATCH (entity)-[:HAS_DOCUMENT]->(document)
                  -[:HAS_CHUNK]->(node)

            RETURN
                labels(entity) AS entity_type,
                entity.name AS entity_name,
                document.file_name AS document,
                node.text AS chunk,
                score

            ORDER BY score DESC
            """,
            top_k=top_k,
            embedding=embedding,
        )

        results = []

        for record in vector_result:

            entity_type = record["entity_type"]
            entity_name = record["entity_name"]

            graph_context = get_graph_context(
                session,
                entity_name,
                entity_type,
            )

            results.append(
                {
                    "entity_type": entity_type,
                    "entity_name": entity_name,
                    "document": record["document"],
                    "chunk": record["chunk"],
                    "score": record["score"],
                    **graph_context,
                }
            )

        return results


def print_results(results):

    print("\n==============================")
    print("GRAPH RAG SEARCH")
    print("==============================")

    for i, result in enumerate(results, start=1):

        print(f"\n----------- RESULT {i} -----------")

        print("Entity:")
        print(result["entity_name"])

        print("Type:")
        print(result["entity_type"])

        print("Similarity:")
        print(round(result["score"], 4))

        print("\nEmployee Skills:")
        print(result["employee_skills"])

        print("\nWorked On:")
        print(result["worked_projects"])

        print("\nRequired Skills:")
        print(result["required_skills"])

        print("\nTasks:")
        print(result["tasks"])

        print("\nAssigned Projects:")
        print(result["assigned_projects"])

        print("\nDocument:")
        print(result["document"])

        print("\nRelevant Text:")
        print(result["chunk"])


if __name__ == "__main__":

    question = (
        "Who has experience building "
        "RAG applications and AI assistants?"
    )

    results = search_graph_rag(question)

    print_results(results)