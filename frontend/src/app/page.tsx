"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Menu, CheckCircle2, AlertCircle, Info, Sparkles } from "lucide-react";
import Sidebar from "../components/Sidebar";
import WorkforceMetrics from "../components/WorkforceMetrics";
import AssistantHome from "../components/AssistantHome";
import EmployeesView from "../components/EmployeesView";
import ProjectsView from "../components/ProjectsView";
import AssignmentsView from "../components/AssignmentsView";
import AddEmployeeModal from "../components/AddEmployeeModal";
import AddProjectModal from "../components/AddProjectModal";
import UploadDocumentModal from "../components/UploadDocumentModal";
import {
  Employee,
  Project,
  EmployeeAvailability,
  NavigationPage,
  AssistantTurn,
  ToastMessage,
} from "../types";
import { fetchEmployees, fetchProjects, fetchAvailability } from "../lib/api";

function generateUUID(): string {
  return "conv-" + Math.random().toString(36).substring(2, 11) + "-" + Date.now().toString(36);
}

export default function WorkGraphApp() {
  const [currentPage, setCurrentPage] = useState<NavigationPage>("overview");
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // Workforce Live Data
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [availability, setAvailability] = useState<EmployeeAvailability[]>([]);
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  // Conversation State
  const [conversationId, setConversationId] = useState<string>("");
  const [messages, setMessages] = useState<AssistantTurn[]>([]);
  const [recentConversations, setRecentConversations] = useState<
    { id: string; title: string; messages: AssistantTurn[] }[]
  >([]);

  // Toasts
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((message: string, type: ToastMessage["type"] = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  }, []);

  // Fetch initial workforce data
  const loadData = useCallback(async () => {
    try {
      const [empData, projData, availData] = await Promise.all([
        fetchEmployees(),
        fetchProjects(),
        fetchAvailability(),
      ]);
      setEmployees(empData);
      setProjects(projData);
      setAvailability(availData);
    } catch (err: any) {
      addToast(err.message || "Could not connect to FastAPI backend.", "error");
    } finally {
      setIsInitialLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadData();
    const newId = generateUUID();
    setConversationId(newId);
  }, [loadData]);

  // Handle New Chat
  const handleNewChat = () => {
    if (messages.length > 0) {
      // archive current conversation to recent
      const firstUserMessage = messages.find((m) => m.role === "user");
      const title = firstUserMessage
        ? firstUserMessage.content.slice(0, 36) + (firstUserMessage.content.length > 36 ? "..." : "")
        : "Conversation";

      setRecentConversations((prev) => [
        { id: conversationId, title, messages: [...messages] },
        ...prev.filter((c) => c.id !== conversationId),
      ]);
    }

    const nextId = generateUUID();
    setConversationId(nextId);
    setMessages([]);
    setCurrentPage("overview");
    addToast("Started a new conversation session.", "info");
  };

  const handleSelectRecentChat = (id: string) => {
    const found = recentConversations.find((c) => c.id === id);
    if (found) {
      setConversationId(found.id);
      setMessages(found.messages);
      setCurrentPage("overview");
    }
  };

  const handleAssistantMessage = (userText: string, assistantText: string, newConvId?: string) => {
    if (newConvId) {
      setConversationId(newConvId);
    }
    const updatedMessages: AssistantTurn[] = [
      ...messages,
      { role: "user", content: userText },
      { role: "assistant", content: assistantText },
    ];
    setMessages(updatedMessages);

    // Keep title updated in recent chats
    const firstUserMsg = updatedMessages.find((m) => m.role === "user");
    const title = firstUserMsg
      ? firstUserMsg.content.slice(0, 36) + (firstUserMsg.content.length > 36 ? "..." : "")
      : "Conversation";

    const convKey = newConvId || conversationId;
    setRecentConversations((prev) => [
      { id: convKey, title, messages: updatedMessages },
      ...prev.filter((c) => c.id !== convKey),
    ]);
  };

  const viewTitles: Record<NavigationPage, string> = {
    overview: "Workforce Overview",
    employees: "Employees Directory",
    projects: "Project Portfolio",
    assignments: "Staffing & Assignments",
    add_employee: "Add Employee",
    add_project: "Add Project",
    upload_employee_doc: "Upload Employee Document",
    upload_project_doc: "Upload Project Document",
  };

  return (
    <div className="app-container">
      {/* Persistent Dark Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onSelectPage={(page) => setCurrentPage(page)}
        onNewChat={handleNewChat}
        isOpenMobile={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        recentChats={recentConversations.map((c) => ({ id: c.id, title: c.title }))}
        onSelectChat={handleSelectRecentChat}
        activeChatId={conversationId}
      />

      {/* Main Workspace Area */}
      <main className="main-wrapper">
        {/* Sticky Top Bar */}
        <header className="top-bar">
          <div className="top-bar-left">
            <button
              className="btn-mobile-toggle"
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
            >
              <Menu size={18} />
            </button>
            <h1 className="current-view-title">{viewTitles[currentPage]}</h1>
            <span className="workspace-badge">Live Neo4j Graph</span>
          </div>
          <div>
            <span
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-muted)",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <span className="status-dot"></span>
              FastAPI :8000
            </span>
          </div>
        </header>

        {/* Content Body */}
        <div className="content-body">
          {/* Always show Live Metrics on Overview */}
          {currentPage === "overview" && (
            <>
              <WorkforceMetrics
                employees={employees}
                projects={projects}
                availability={availability}
              />
              <div className="nb-card" style={{ padding: "24px 28px" }}>
                <AssistantHome
                  conversationId={conversationId}
                  messages={messages}
                  onSendMessage={handleAssistantMessage}
                  onResetChat={handleNewChat}
                  onError={(err) => addToast(err, "error")}
                />
              </div>
            </>
          )}

          {currentPage === "employees" && (
            <EmployeesView employees={employees} availability={availability} />
          )}

          {currentPage === "projects" && (
            <ProjectsView
              projects={projects}
              onError={(err) => addToast(err, "error")}
            />
          )}

          {currentPage === "assignments" && (
            <AssignmentsView
              projects={projects}
              availability={availability}
              onRefreshData={loadData}
              onSuccess={(msg) => addToast(msg, "success")}
              onError={(msg) => addToast(msg, "error")}
            />
          )}

          {/* Modal / Feature Views */}
          {currentPage === "add_employee" && (
            <AddEmployeeModal
              onClose={() => setCurrentPage("employees")}
              onSuccess={(msg) => {
                addToast(msg, "success");
                setCurrentPage("employees");
              }}
            />
          )}

          {currentPage === "add_project" && (
            <AddProjectModal
              onClose={() => setCurrentPage("projects")}
              onSuccess={(msg) => {
                addToast(msg, "success");
                setCurrentPage("projects");
              }}
            />
          )}

          {currentPage === "upload_employee_doc" && (
            <UploadDocumentModal
              type="employee"
              onClose={() => setCurrentPage("employees")}
              onSuccess={(msg) => {
                addToast(msg, "success");
                setCurrentPage("employees");
              }}
            />
          )}

          {currentPage === "upload_project_doc" && (
            <UploadDocumentModal
              type="project"
              onClose={() => setCurrentPage("projects")}
              onSuccess={(msg) => {
                addToast(msg, "success");
                setCurrentPage("projects");
              }}
            />
          )}
        </div>
      </main>

      {/* Floating Toast Alerts */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.type === "success" && <CheckCircle2 size={16} color="var(--green-primary)" />}
            {t.type === "error" && <AlertCircle size={16} color="#b91c1c" />}
            {t.type === "info" && <Info size={16} color="var(--purple-primary)" />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
