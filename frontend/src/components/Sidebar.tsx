"use client";

import React, { useState } from "react";
import {
  MessageSquarePlus,
  Search,
  LayoutDashboard,
  Users,
  Briefcase,
  UserCheck,
  UserPlus,
  FolderPlus,
  FileUp,
  Files,
  X,
  Sparkles,
} from "lucide-react";
import { NavigationPage } from "../types";

interface SidebarProps {
  currentPage: NavigationPage;
  onSelectPage: (page: NavigationPage) => void;
  onNewChat: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  recentChats: { id: string; title: string }[];
  onSelectChat: (id: string) => void;
  activeChatId: string;
}

export default function Sidebar({
  currentPage,
  onSelectPage,
  onNewChat,
  isOpenMobile,
  onCloseMobile,
  recentChats,
  onSelectChat,
  activeChatId,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredChats = recentChats.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const navItems: { id: NavigationPage; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Workforce Overview", icon: <LayoutDashboard size={16} /> },
    { id: "employees", label: "Employees", icon: <Users size={16} /> },
    { id: "projects", label: "Projects", icon: <Briefcase size={16} /> },
    { id: "assignments", label: "Assign Employee to Project", icon: <UserCheck size={16} /> },
    { id: "add_employee", label: "Add Employee", icon: <UserPlus size={16} /> },
    { id: "add_project", label: "Add Project", icon: <FolderPlus size={16} /> },
    { id: "upload_employee_doc", label: "Upload Employee Resume/Document", icon: <FileUp size={16} /> },
    { id: "upload_project_doc", label: "Upload Project Document", icon: <Files size={16} /> },
  ];

  return (
    <>
      <aside className={`sidebar ${isOpenMobile ? "open" : ""}`}>
        <div className="sidebar-header">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div className="sidebar-brand">
              <div className="brand-icon-box">W</div>
              <div>
                <div className="brand-title">WorkGraph</div>
                <div className="brand-subtitle">Workforce intelligence</div>
              </div>
            </div>
            {isOpenMobile && (
              <button
                onClick={onCloseMobile}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#949aa7",
                  cursor: "pointer",
                }}
              >
                <X size={20} />
              </button>
            )}
          </div>
        </div>

        <div className="sidebar-action-area">
          <button className="btn-new-chat" onClick={onNewChat}>
            <MessageSquarePlus size={16} />
            <span>+ New chat</span>
          </button>

          <div className="sidebar-search-wrap">
            <Search size={14} className="sidebar-search-icon" />
            <input
              type="text"
              placeholder="Search conversations"
              className="sidebar-search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="sidebar-nav-section">
          <div className="nav-section-title">WORKSPACE</div>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentPage === item.id ? "active" : ""}`}
              onClick={() => {
                onSelectPage(item.id);
                onCloseMobile();
              }}
            >
              {item.icon}
              <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {item.label}
              </span>
            </button>
          ))}

          <div className="nav-section-title" style={{ marginTop: "16px" }}>
            RECENT CONVERSATIONS
          </div>
          <div className="sidebar-recent-chats">
            {filteredChats.length > 0 ? (
              filteredChats.map((chat) => (
                <div
                  key={chat.id}
                  className="recent-chat-item"
                  style={{
                    backgroundColor: chat.id === activeChatId ? "#22232a" : "transparent",
                    color: chat.id === activeChatId ? "#ffffff" : "#9aa1b0",
                    fontWeight: chat.id === activeChatId ? 600 : 400,
                  }}
                  onClick={() => {
                    onSelectChat(chat.id);
                    onCloseMobile();
                  }}
                >
                  <Sparkles size={12} color="#a78bfa" />
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{chat.title}</span>
                </div>
              ))
            ) : (
              <div style={{ fontSize: "11px", color: "#64748b", padding: "6px 8px" }}>
                {searchQuery ? "No matches" : "New conversation"}
              </div>
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="graph-status-badge">
            <span className="status-dot"></span>
            <span>Neo4j Live Connected</span>
          </div>
        </div>
      </aside>
    </>
  );
}
