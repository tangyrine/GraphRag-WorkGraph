from pathlib import Path

from document_processor import process_document
from neo4j_client import driver


ROLE_NAME_MAP = {
    "Ai Engineer": "AI Engineer",
    "Backend Developer": "Backend Developer",
    "Cybersecurity Engineer": "Cybersecurity Engineer",
    "Data Engineer": "Data Engineer",
    "Devops Engineer": "DevOps Engineer",
    "Frontend Developer": "Frontend Developer",
}


def filename_to_entity_name(file_path, entity_type):
    name = Path(file_path).stem

    if entity_type == "Employee":
        name = name.replace("_profile", "")

    name = name.replace("_", " ").title()

    if entity_type == "Role":
        name = ROLE_NAME_MAP.get(name, name)

    return name


def find_or_create_entity(
    session,
    entity_name,
    entity_type,
):
    """
    Find an existing Employee/Role/Project.

    For Project documents, create the Project if it
    does not already exist.
    """

    result = session.run(
        f"""
        MATCH (e:{entity_type} {{name: $entity_name}})
        RETURN e
        LIMIT 1
        """,
        entity_name=entity_name,
    ).single()

    if result:
        return "existing"

    if entity_type == "Project":
        session.run(
            """
            CREATE (:Project {
                name: $entity_name
            })
            """,
            entity_name=entity_name,
        )

        return "created"

    if entity_type == "Employee":
        session.run(
            """
            CREATE (:Employee {
                name: $entity_name
            })
            """,
            entity_name=entity_name,
        )

        return "created"

    raise ValueError(
        f"{entity_type} '{entity_name}' "
        "does not exist in Neo4j."
    )


def ingest_document(
    file_path,
    entity_name,
    entity_type,
):
    """
    Ingest one TXT/PDF document into Neo4j.
    """

    processed = process_document(file_path)

    file_name = processed["file_name"]
    chunks = processed["chunks"]
    embeddings = processed["embeddings"]

    with driver.session() as session:

        entity_status = find_or_create_entity(
            session,
            entity_name,
            entity_type,
        )

        # Prevent duplicate ingestion.
        existing_document = session.run(
            f"""
            MATCH (e:{entity_type} {{name: $entity_name}})
                  -[:HAS_DOCUMENT]->(d:Document)
            WHERE d.file_name = $file_name
            RETURN d
            LIMIT 1
            """,
            entity_name=entity_name,
            file_name=file_name,
        ).single()

        if existing_document:
            return {
                "file_name": file_name,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "chunks_created": 0,
                "status": "already_exists",
            }

        # Create Document node.
        document = session.run(
            """
            CREATE (d:Document {
                file_name: $file_name
            })
            RETURN elementId(d) AS id
            """,
            file_name=file_name,
        ).single()

        document_id = document["id"]

        # Connect Entity -> Document.
        session.run(
            f"""
            MATCH (e:{entity_type} {{name: $entity_name}})
            MATCH (d:Document)
            WHERE elementId(d) = $document_id

            CREATE (e)-[:HAS_DOCUMENT]->(d)
            """,
            entity_name=entity_name,
            document_id=document_id,
        )

        # Create chunks.
        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            session.run(
                """
                MATCH (d:Document)
                WHERE elementId(d) = $document_id

                CREATE (c:Chunk {
                    chunk_index: $chunk_index,
                    text: $text,
                    embedding: $embedding
                })

                CREATE (d)-[:HAS_CHUNK]->(c)
                """,
                document_id=document_id,
                chunk_index=index,
                text=chunk,
                embedding=embedding,
            )

    return {
        "file_name": file_name,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "chunks_created": len(chunks),
        "status": "ingested",
        "entity_status": entity_status,
    }


def ingest_directory(
    directory,
    entity_type,
):
    directory_path = Path(directory)

    if not directory_path.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    results = []

    for file_path in sorted(directory_path.iterdir()):

        if file_path.suffix.lower() not in {
            ".txt",
            ".pdf",
        }:
            continue

        entity_name = filename_to_entity_name(
            file_path,
            entity_type,
        )

        print(
            f"\nProcessing {entity_type}: "
            f"{entity_name}"
        )

        try:
            result = ingest_document(
                file_path=str(file_path),
                entity_name=entity_name,
                entity_type=entity_type,
            )

            print(result)
            results.append(result)

        except Exception as exc:

            print(
                f"ERROR: {file_path.name}: {exc}"
            )

            results.append({
                "file_name": file_path.name,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "status": "error",
                "error": str(exc),
            })

    return results


if __name__ == "__main__":

    base = Path("data/graphrag")

    print("\n==============================")
    print("INGESTING EMPLOYEE DOCUMENTS")
    print("==============================")

    employee_results = ingest_directory(
        base / "employees",
        "Employee",
    )

    print("\n==============================")
    print("INGESTING PROJECT DOCUMENTS")
    print("==============================")

    project_results = ingest_directory(
        base / "projects",
        "Project",
    )

    print("\n==============================")
    print("INGESTING ROLE DOCUMENTS")
    print("==============================")

    role_results = ingest_directory(
        base / "roles",
        "Role",
    )

    all_results = (
        employee_results
        + project_results
        + role_results
    )

    ingested = sum(
        r["status"] == "ingested"
        for r in all_results
    )

    existing = sum(
        r["status"] == "already_exists"
        for r in all_results
    )

    errors = sum(
        r["status"] == "error"
        for r in all_results
    )

    print("\n==============================")
    print("INGESTION SUMMARY")
    print("==============================")
    print(f"Ingested: {ingested}")
    print(f"Already existed: {existing}")
    print(f"Errors: {errors}")