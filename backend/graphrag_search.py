from sentence_transformers import SentenceTransformer
from neo4j_client import driver


model = SentenceTransformer("all-MiniLM-L6-v2")


def search_graph_rag(question: str, top_k: int = 5):

    embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    with driver.session() as session:

        result = session.run(
            """
            CALL db.index.vector.queryNodes(
                'chunk_embedding_index',
                $top_k,
                $embedding
            )
            YIELD node, score

            MATCH (entity)-[:HAS_DOCUMENT]->(document)
                  -[:HAS_CHUNK]->(node)

            OPTIONAL MATCH (entity)-[:HAS_SKILL]->(skill)
            WITH entity, document, node, score,
                 collect(DISTINCT skill.name) AS employee_skills

            OPTIONAL MATCH (entity)-[:WORKED_ON]->(worked_project)
            WITH entity, document, node, score,
                 employee_skills,
                 collect(DISTINCT worked_project.name) AS worked_projects

            OPTIONAL MATCH (entity)-[:ASSIGNED_TO]->(assigned_project)
            WITH entity, document, node, score,
                 employee_skills,
                 worked_projects,
                 collect(DISTINCT assigned_project.name) AS assigned_projects

            OPTIONAL MATCH (entity)-[:REQUIRES]->(required_skill)
            WITH entity, document, node, score,
                 employee_skills,
                 worked_projects,
                 assigned_projects,
                 collect(DISTINCT required_skill.name) AS required_skills

            RETURN
                labels(entity) AS entity_type,
                entity.name AS entity_name,
                entity.role AS role,
                entity.department AS department,
                document.file_name AS document,
                node.text AS chunk,
                score,
                employee_skills,
                worked_projects,
                assigned_projects,
                required_skills

            ORDER BY score DESC
            """,
            top_k=top_k,
            embedding=embedding,
        )

        return [record.data() for record in result]