import os
import sys
sys.path.append("backend")

from backend.ai_workflow import app as ai_workflow
from backend.neo4j_client import run_query
import requests

API_URL = "http://127.0.0.1:8000"

print("==========================================")
print("RUNNING 7 MANDATORY TEST SUITES FOR WORKGRAPH AI")
print("==========================================")

# TEST 1
print("\n--- TEST 1: Who has experience with RAG? ---")
res1 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Who has experience with RAG?",
    "conversation_id": "test-suite-1"
}).json()
print("ANSWER 1:\n", res1["answer"])

# TEST 2 (Ambiguity & Pronoun Resolution)
print("\n--- TEST 2A: Ambiguous Pronoun Clarification ---")
# Suppose history has Alice and Priya (or multiple candidates)
res2a = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Can she work on a RAG-based chatbot?",
    "conversation_id": "test-suite-1"
}).json()
print("ANSWER 2A:\n", res2a["answer"])

print("\n--- TEST 2B: Unambiguous Pronoun Resolution ---")
res2_setup = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Tell me about David",
    "conversation_id": "test-suite-2"
}).json()
res2b = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Can he work on a RAG-based chatbot?",
    "conversation_id": "test-suite-2"
}).json()
print("ANSWER 2B:\n", res2b["answer"])

# TEST 3
print("\n--- TEST 3: Who should work on a RAG-based chatbot? ---")
res3 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Who should work on a RAG-based chatbot?",
    "conversation_id": "test-suite-3"
}).json()
print("ANSWER 3:\n", res3["answer"])

# TEST 4 (Assign and re-query)
print("\n--- TEST 4: Assign candidate and re-query ---")
# First unassign David to start clean, then assign David to "Cloud Migration"
requests.post(f"{API_URL}/employees/David/unassign")
assign_res = requests.post(f"{API_URL}/employees/David/assign/Cloud%20Migration").json()
print("Assign result:", assign_res)

res4 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Who should work on a RAG-based chatbot?",
    "conversation_id": "test-suite-4"
}).json()
print("ANSWER 4 (After David assigned):\n", res4["answer"])
# Clean up David's assignment
requests.post(f"{API_URL}/employees/David/unassign")

# TEST 5
print("\n--- TEST 5: Are there any available employees with the required skills? ---")
res5 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Are there any available employees with the required skills for the AI Customer Assistant project?",
    "conversation_id": "test-suite-5"
}).json()
print("ANSWER 5:\n", res5["answer"])

# TEST 6
print("\n--- TEST 6: Who has the best match? ---")
res6 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Who has the best match for the Cloud Migration project?",
    "conversation_id": "test-suite-6"
}).json()
print("ANSWER 6:\n", res6["answer"])

# TEST 7
print("\n--- TEST 7: Who is available? ---")
res7 = requests.post(f"{API_URL}/ai/assistant", json={
    "question": "Who is available?",
    "conversation_id": "test-suite-7"
}).json()
print("ANSWER 7:\n", res7["answer"])

print("\n==========================================")
print("ALL 7 TEST SUITES COMPLETED")
print("==========================================")
