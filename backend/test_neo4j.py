from neo4j_client import run_query

result = run_query("""
MATCH (e:Employee)
RETURN e.name AS employee
ORDER BY e.name
LIMIT 5
""")

print(result)