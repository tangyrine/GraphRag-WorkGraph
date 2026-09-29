from uuid import uuid4

import requests
import streamlit as st


API_URL = "http://backend:8000"

st.set_page_config(
    page_title="WorkGraph AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, input, textarea, button, label { font-family: 'Poppins', sans-serif !important; }
    .stApp { background: #f3f3f0; color: #171717; }
    .block-container { max-width: 1420px; min-height: calc(100vh - 2.5rem); margin: 1.2rem 1.5rem;
        padding: 2rem 2.6rem 3rem; background: #ffffff; border: 1px solid #e6e6e1; border-radius: 24px;
        box-shadow: 0 14px 38px rgba(16, 16, 16, .05); }
    [data-testid="stSidebar"] { background: #121212 !important; border: 0; }
    [data-testid="stSidebar"] > div:first-child { background: #121212; padding: 1.35rem .9rem; }
    [data-testid="stSidebar"] * { color: #f4f4ef; }
    [data-testid="stSidebar"] .stTextInput input { background: #222; border: 1px solid #363636; color: #fff; }
    [data-testid="stSidebar"] .stButton > button { background: #202020; color: #f6f6f2; border: 1px solid #363636; }
    [data-testid="stSidebar"] .stButton > button:hover { border-color: #c8ff00; color: #c8ff00; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 3px; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { border-radius: 8px; padding: 8px 10px; font-size: 12px; font-weight: 500; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: #202020; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background: #232323; color: #ffffff; }
    [data-testid="stSidebar"] input[type="radio"] { accent-color: #c8ff00; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: inherit; }
    .brand { display:flex; gap:11px; align-items:center; margin: .2rem .35rem 1.75rem; }
    .brand-mark { width:34px; height:34px; display:grid; place-items:center; border-radius:10px; background:#c8ff00;
        color:#111; font-size:14px; font-weight:800; }
    .brand-name { font-size:17px; font-weight:700; letter-spacing:-.4px; }
    .brand-copy { font-size:10px; color:#92928c; margin-top:1px; }
    .sidebar-label { font-size:10px; font-weight:700; letter-spacing:1px; color:#777770; text-transform:uppercase; margin:1.2rem .45rem .35rem; }
    .page-kicker { color:#6c6c66; font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:7px; }
    .page-title { font-size:30px; line-height:1.12; font-weight:700; letter-spacing:-1.1px; color:#141414; }
    .page-copy { font-size:13px; color:#777771; max-width:680px; margin-top:8px; }
    .metric-card, .surface-card { background:#fff; border:1px solid #e8e8e3; border-radius:15px; box-shadow:0 7px 18px rgba(0,0,0,.025); }
    .metric-card { padding:1rem 1.05rem; min-height:96px; }
    .metric-label { font-size:9px; font-weight:700; letter-spacing:1px; color:#8a8a84; text-transform:uppercase; }
    .metric-value { font-size:25px; color:#151515; font-weight:700; letter-spacing:-.9px; margin-top:5px; }
    .metric-note { font-size:10px; color:#85857f; }
    .section-title { color:#191919; font-size:17px; font-weight:700; letter-spacing:-.25px; margin:1.7rem 0 .2rem; }
    .section-copy { color:#777771; font-size:11px; margin-bottom:.8rem; }
    .workspace-bar { display:flex; justify-content:space-between; align-items:center; padding-bottom:1rem; border-bottom:1px solid #edede9; }
    .workspace-name { color:#1a1a1a; font-size:15px; font-weight:700; }
    .workspace-status { color:#777771; font-size:11px; }
    .welcome { text-align:center; padding: 5rem 1rem 1.6rem; }
    .welcome h1 { margin:0; color:#121212; font-size:44px; letter-spacing:-2px; line-height:1.05; }
    .welcome p { margin:12px auto 0; max-width:610px; color:#85857f; font-size:15px; }
    .capability { display:inline-block; border:1px solid #e5e5e0; background:#fbfbf9; border-radius:99px; color:#696963;
        padding:4px 9px; margin:15px 3px 0; font-size:10px; font-weight:600; }
    .suggestion-card { min-height:126px; padding:17px 17px 13px; background:#fff; border:1px solid #ebebe7; border-radius:15px;
        box-shadow:0 6px 18px rgba(0,0,0,.025); }
    .suggestion-number { width:26px; height:26px; display:grid; place-items:center; border-radius:7px; background:#c8ff00;
        color:#171717; font-size:11px; font-weight:800; margin-bottom:12px; }
    .suggestion-title { color:#191919; font-size:14px; font-weight:700; }
    .suggestion-copy { color:#777771; font-size:11px; line-height:1.35; margin-top:4px; }
    .empty-card { text-align:center; padding:2.3rem 1.2rem; color:#73736d; }
    .stButton > button { border-radius:10px; font-size:11px; font-weight:600; min-height:38px; border:1px solid #deded9; background:#fff; color:#202020; }
    .stButton > button:hover { border-color:#9bbd00; color:#1c2600; background:#faffdc; }
    div.st-key-sidebar_new_chat .stButton > button, div.st-key-new_chat .stButton > button,
    div.st-key-suggestion_1 .stButton > button, div.st-key-suggestion_2 .stButton > button,
    div.st-key-suggestion_3 .stButton > button { background:#c8ff00; border-color:#c8ff00; color:#171717; }
    div.st-key-sidebar_new_chat .stButton > button:hover, div.st-key-new_chat .stButton > button:hover,
    div.st-key-suggestion_1 .stButton > button:hover, div.st-key-suggestion_2 .stButton > button:hover,
    div.st-key-suggestion_3 .stButton > button:hover { background:#d5ff42; border-color:#d5ff42; color:#171717; }
    [data-testid="stChatMessage"] { margin: 14px auto; max-width:860px; padding: 4px 2px; border:0; background:transparent; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { color:#252525; font-size:13px; line-height:1.75; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:#f4f4f0; border:1px solid #e9e9e4; border-radius:15px; padding: 10px 14px; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { padding: 10px 4px; }
    [data-testid="stChatInput"] { max-width:860px; margin-left:auto; margin-right:auto; }
    [data-testid="stChatInput"] textarea { min-height:54px; border-radius:15px !important; background:#fff; border-color:#deded9; font-size:13px !important; }
    [data-testid="stChatInput"] button { background:#c8ff00 !important; border-color:#c8ff00 !important; color:#171717 !important; border-radius:10px !important; }
    [data-testid="stChatInput"] button:hover { background:#d5ff42 !important; border-color:#d5ff42 !important; }
    [data-testid="stDataFrame"] { border:1px solid #e8e8e3; border-radius:12px; overflow:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_data(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=20)
    response.raise_for_status()
    return response.json()


def load_workforce_data():
    try:
        employees = fetch_data("/employees")
        projects = fetch_data("/projects")
        availability = fetch_data("/employees/availability")
        return employees, projects, availability
    except requests.exceptions.RequestException:
        st.error("Could not connect to the FastAPI backend. Make sure it is running.")
        st.stop()


def initialize_conversation():
    if "assistant_conversation_id" not in st.session_state:
        st.session_state.assistant_conversation_id = str(uuid4())
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []


def reset_conversation():
    st.session_state.assistant_conversation_id = str(uuid4())
    st.session_state.assistant_messages = []


def render_metrics(employees, projects, availability):
    available = sum(item["status"] == "Available" for item in availability)
    departments = len({employee["department"] for employee in employees})
    metrics = [
        ("Employees", len(employees), "Workforce directory"),
        ("Projects", len(projects), "Project portfolio"),
        ("Departments", departments, "Across the organization"),
        ("Available", available, "Ready for assignment"),
    ]
    columns = st.columns(4)
    for column, (label, value, note) in zip(columns, metrics):
        with column:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>""",
                unsafe_allow_html=True,
            )


def render_assistant():
    st.markdown(
        """<div class="workspace-bar"><div><div class="workspace-name">Workforce Intelligence Assistant</div>
        <div class="workspace-status">Graph-aware workforce guidance</div></div>
        <div class="workspace-status">Live organizational context</div></div>""",
        unsafe_allow_html=True,
    )
    header_left, header_right = st.columns([5, 1])
    with header_left:
        st.caption("Conversations use workforce graph data, organizational documents, current assignments, and prior context.")
    with header_right:
        if st.button("New chat", use_container_width=True, key="new_chat"):
            reset_conversation()
            st.rerun()

    if not st.session_state.assistant_messages:
        st.markdown(
            """<div class="welcome"><h1>WorkGraph AI</h1><p>Workforce intelligence, powered by your graph and organizational documents.</p>
            <span class="capability">Workforce graph</span><span class="capability">Workforce documents</span>
            <span class="capability">Current assignment state</span><span class="capability">Conversation context</span></div>""",
            unsafe_allow_html=True,
        )
        suggestions = [
            ("Find the right team", "Match employees to project requirements.", "Who should work on the AI Customer Assistant project and why?"),
            ("Analyze skill gaps", "Identify missing or scarce workforce skills.", "What are the skill gaps for the AI Customer Assistant project?"),
            ("Explore workforce", "Ask about employees, projects, skills, and assignments.", "Who has experience with LangGraph and is currently available?"),
        ]
        suggestion_columns = st.columns(3)
        for index, (column, (title, copy, prompt)) in enumerate(zip(suggestion_columns, suggestions), start=1):
            with column:
                st.markdown(
                    f"""<div class="suggestion-card"><div class="suggestion-number">{index}</div>
                    <div class="suggestion-title">{title}</div><div class="suggestion-copy">{copy}</div></div>""",
                    unsafe_allow_html=True,
                )
                if st.button("Try this", key=f"suggestion_{index}", use_container_width=True):
                    st.session_state.pending_assistant_question = prompt
                    st.rerun()

    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.session_state.pop("pending_assistant_question", None)
    if question is None:
        question = st.chat_input("Ask about employees, projects, skills, or staffing")
    if not question:
        return

    st.session_state.assistant_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing workforce knowledge..."):
            try:
                response = requests.post(
                    f"{API_URL}/ai/assistant",
                    json={
                        "question": question,
                        "conversation_id": st.session_state.assistant_conversation_id,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("answer", "No answer returned.")
                st.session_state.assistant_conversation_id = data.get(
                    "conversation_id", st.session_state.assistant_conversation_id
                )
                st.session_state.assistant_messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.markdown(answer)
            except requests.exceptions.Timeout:
                st.error("The AI request took too long. Please try again.")
            except requests.exceptions.RequestException:
                st.error("Could not reach the unified assistant. Please try again.")


def render_employees(employees, availability):
    st.markdown('<div class="page-kicker">Workforce directory</div><div class="page-title">Employees</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-copy">Browse the workforce and current Neo4j-backed availability.</div>', unsafe_allow_html=True)
    availability_by_name = {item["employee"]: item for item in availability}
    rows = []
    for employee in employees:
        assignment = availability_by_name.get(employee["name"], {})
        rows.append({
            **employee,
            "availability": assignment.get("status", "Unknown"),
            "current_project": assignment.get("current_project") or "—",
        })
    st.markdown('<div class="section-title">Employee directory</div>', unsafe_allow_html=True)
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_projects(projects):
    st.markdown('<div class="page-kicker">Project portfolio</div><div class="page-title">Projects</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-copy">Review project status, staffing fit, and skill coverage.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Project directory</div>', unsafe_allow_html=True)
    st.dataframe(projects, use_container_width=True, hide_index=True)

    project_names = [project["name"] for project in projects]
    if not project_names:
        st.info("No projects are available for analysis.")
        return
    st.markdown('<div class="section-title">Project intelligence</div><div class="section-copy">Compare requirements with currently available employees.</div>', unsafe_allow_html=True)
    selection, action = st.columns([4, 1])
    with selection:
        project_name = st.selectbox("Project", project_names, key="project_analysis")
    with action:
        st.write("")
        analyze = st.button("Analyze", use_container_width=True, key="analyze_project")
    if not analyze:
        return
    try:
        matches = fetch_data(f"/projects/{project_name}/match")
        gaps = fetch_data(f"/projects/{project_name}/skill-gaps")
    except requests.exceptions.RequestException:
        st.error("Unable to analyze this project.")
        return
    left, right = st.columns(2)
    with left:
        st.markdown("#### Recommended available people")
        if matches:
            st.dataframe(matches, use_container_width=True, hide_index=True)
        else:
            st.info("No available employees match this project.")
    with right:
        st.markdown("#### Skill coverage")
        st.dataframe(gaps, use_container_width=True, hide_index=True)


def render_assignments(projects, availability):
    st.markdown('<div class="page-kicker">Workforce operations</div><div class="page-title">Assign employee to project</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-copy">Assignments update Neo4j directly. Availability shown here is always refreshed from the graph.</div>', unsafe_allow_html=True)
    available = [item for item in availability if item["status"] == "Available"]
    project_names = [project["name"] for project in projects]
    st.markdown('<div class="section-title">New assignment</div>', unsafe_allow_html=True)
    if available and project_names:
        employee_column, project_column, action_column = st.columns([2, 2, 1])
        with employee_column:
            employee_name = st.selectbox("Employee", [item["employee"] for item in available])
        with project_column:
            project_name = st.selectbox("Project", project_names, key="assignment_project")
        with action_column:
            st.write("")
            assign = st.button("Assign", use_container_width=True)
        if assign:
            try:
                response = requests.post(
                    f"{API_URL}/employees/{employee_name}/assign/{project_name}", timeout=30
                )
                response.raise_for_status()
                result = response.json()
                if result.get("success"):
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result.get("message", "Assignment failed."))
            except requests.exceptions.RequestException:
                st.error("Unable to assign employee.")
    else:
        st.info("There are no available employees or projects to assign.")

    assigned = [item for item in availability if item["status"] == "Assigned"]
    st.markdown('<div class="section-title">Current assignments</div>', unsafe_allow_html=True)
    if not assigned:
        st.info("No employees are currently assigned to projects.")
        return
    for employee in assigned:
        name_column, project_column, action_column = st.columns([2, 2, 1])
        with name_column:
            st.markdown(f"**{employee['employee']}**  \n{employee['role']}")
        with project_column:
            st.write(employee["current_project"])
        with action_column:
            if st.button("Unassign", key=f"unassign_{employee['employee']}", use_container_width=True):
                try:
                    response = requests.post(
                        f"{API_URL}/employees/{employee['employee']}/unassign", timeout=30
                    )
                    response.raise_for_status()
                    st.success(f"{employee['employee']} is now available.")
                    st.rerun()
                except requests.exceptions.RequestException:
                    st.error("Unable to unassign employee.")


def render_unavailable_feature(title, description):
    st.markdown(f'<div class="page-kicker">Workforce operations</div><div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-copy">{description}</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="surface-card empty-card"><strong>This action is not exposed by the current backend.</strong><br>
        The UI does not create local records or simulate ingestion; Neo4j-backed operations require an existing API.</div>""",
        unsafe_allow_html=True,
    )


initialize_conversation()
employees, projects, availability = load_workforce_data()

with st.sidebar:
    st.markdown("""<div class="brand"><div class="brand-mark">W</div><div><div class="brand-name">WorkGraph</div><div class="brand-copy">Workforce intelligence</div></div></div>""", unsafe_allow_html=True)
    if st.button("＋  New chat", key="sidebar_new_chat", use_container_width=True):
        reset_conversation()
        st.rerun()
    conversation_search = st.text_input("Search conversations", placeholder="Search conversations", label_visibility="collapsed")
    current_title = next(
        (message["content"] for message in st.session_state.assistant_messages if message["role"] == "user"),
        "New conversation",
    )
    st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        [
            "Workforce Overview",
            "Employees",
            "Projects",
            "Assign Employee to Project",
            "Add Employee",
            "Add Project",
            "Upload Employee Resume/Document",
            "Upload Project Document",
        ],
        label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-label">Data</div>', unsafe_allow_html=True)
    st.caption("Create and upload actions are listed in the workspace navigation.")
    st.markdown('<div class="sidebar-label">Recent</div>', unsafe_allow_html=True)
    if not conversation_search or conversation_search.lower() in current_title.lower():
        st.caption(current_title[:42] + ("…" if len(current_title) > 42 else ""))
    else:
        st.caption("No matching conversations in this browser session.")
    st.markdown('<div class="sidebar-label">Live graph</div>', unsafe_allow_html=True)
    st.caption("Employee availability and assignments are refreshed from Neo4j.")

if page == "Workforce Overview":
    render_assistant()
    st.markdown('<div class="section-title">Live workforce overview</div><div class="section-copy">Current workforce counts are refreshed from the graph on every page load.</div>', unsafe_allow_html=True)
    render_metrics(employees, projects, availability)
elif page == "Employees":
    render_employees(employees, availability)
elif page == "Projects":
    render_projects(projects)
elif page == "Assign Employee to Project":
    render_assignments(projects, availability)
elif page == "Add Employee":
    render_unavailable_feature("Add employee", "Create a workforce record when an employee-creation API is available.")
elif page == "Add Project":
    render_unavailable_feature("Add project", "Create a project record when a project-creation API is available.")
elif page == "Upload Employee Resume/Document":
    render_unavailable_feature("Upload employee document", "Ingest a resume or profile when a document-upload API is available.")
else:
    render_unavailable_feature("Upload project document", "Ingest project knowledge when a document-upload API is available.")
