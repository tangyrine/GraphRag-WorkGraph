"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Send,
  Sparkles,
  User,
  Bot,
  RotateCcw,
  ArrowRight,
  Database,
  FileText,
  Workflow,
  MessageSquare,
  Loader2,
} from "lucide-react";
import { AssistantTurn } from "../types";
import { askAssistant } from "../lib/api";

interface AssistantHomeProps {
  conversationId: string;
  messages: AssistantTurn[];
  onSendMessage: (userText: string, assistantText: string, newConvId?: string) => void;
  onResetChat: () => void;
  onError: (msg: string) => void;
}

export default function AssistantHome({
  conversationId,
  messages,
  onSendMessage,
  onResetChat,
  onError,
}: AssistantHomeProps) {
  const [inputQuestion, setInputQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    {
      number: 1,
      title: "Find the right team",
      copy: "Match employees to project requirements.",
      question: "Who should work on the AI Customer Assistant project and why?",
    },
    {
      number: 2,
      title: "Analyze skill gaps",
      copy: "Identify missing or scarce workforce skills.",
      question: "What are the skill gaps for the AI Customer Assistant project?",
    },
    {
      number: 3,
      title: "Explore workforce",
      copy: "Ask about employees, projects, skills, and assignments.",
      question: "Who has experience with LangGraph and is currently available?",
    },
  ];

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages, isLoading]);

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || inputQuestion.trim();
    if (!textToSend || isLoading) return;

    setInputQuestion("");
    setIsLoading(true);

    try {
      const response = await askAssistant(textToSend, conversationId, messages);
      onSendMessage(textToSend, response.answer, response.conversation_id);
    } catch (err: any) {
      onError(err.message || "Could not reach the workforce intelligence assistant.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "calc(100vh - 160px)" }}>
      {/* Top Bar with Assistant Header and New Chat */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          paddingBottom: "14px",
          borderBottom: "2px solid var(--border-dark)",
          marginBottom: "20px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "19px", fontWeight: 800, color: "#000000", letterSpacing: "-0.4px" }}>
            Workforce Intelligence Assistant
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
            Live context from Neo4j workforce graph, organizational documents, and active assignments.
          </p>
        </div>
        <button
          className="nb-btn nb-btn-purple-subtle"
          onClick={onResetChat}
          title="Start a fresh conversation"
        >
          <RotateCcw size={14} />
          <span>New chat</span>
        </button>
      </div>

      {/* When conversation is empty: Show Hero and 3 Suggestion Cards */}
      {messages.length === 0 ? (
        <div style={{ flex: 1 }}>
          <div className="assistant-hero">
            <h1 className="assistant-hero-title">WorkGraph AI</h1>
            <p className="assistant-hero-desc">
              Workforce intelligence, powered by your graph and organizational documents.
            </p>
            <div className="capability-badges-wrap">
              <span className="capability-badge">
                <Database size={12} style={{ display: "inline", verticalAlign: "-1px", marginRight: 4 }} />
                Workforce graph
              </span>
              <span className="capability-badge">
                <FileText size={12} style={{ display: "inline", verticalAlign: "-1px", marginRight: 4 }} />
                Workforce documents
              </span>
              <span className="capability-badge">
                <Workflow size={12} style={{ display: "inline", verticalAlign: "-1px", marginRight: 4 }} />
                Current assignment state
              </span>
              <span className="capability-badge">
                <MessageSquare size={12} style={{ display: "inline", verticalAlign: "-1px", marginRight: 4 }} />
                Conversation context
              </span>
            </div>
          </div>

          <div className="suggestions-grid">
            {suggestions.map((s) => (
              <div key={s.number} className="suggestion-card">
                <div className="suggestion-card-header">
                  <div className="suggestion-number">{s.number}</div>
                  <div>
                    <div className="suggestion-title">{s.title}</div>
                    <div className="suggestion-copy">{s.copy}</div>
                  </div>
                </div>
                <div style={{ fontSize: "12px", color: "#4b5563", fontStyle: "italic", background: "#f8fafc", padding: "8px 10px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                  "{s.question}"
                </div>
                <button
                  className="btn-try-this"
                  onClick={() => handleSend(s.question)}
                >
                  <span>Try this</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* Active Conversation Stream */
        <div className="chat-conversation-container" style={{ flex: 1 }}>
          {messages.map((turn, index) => (
            <div key={index} className={`chat-turn ${turn.role}`}>
              <div className={`turn-avatar ${turn.role === "user" ? "user-avatar" : "assistant-avatar"}`}>
                {turn.role === "user" ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="turn-bubble">
                {turn.role === "user" ? (
                  <div style={{ fontWeight: 600 }}>{turn.content}</div>
                ) : (
                  <div className="markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{turn.content}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="chat-turn assistant">
              <div className="turn-avatar assistant-avatar">
                <Bot size={18} />
              </div>
              <div className="turn-bubble" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <Loader2 size={18} className="animate-spin" style={{ animation: "spin 1s linear infinite" }} />
                <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                  Analyzing workforce knowledge graph & documents...
                </span>
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>
      )}

      {/* Sticky Bottom Chat Input */}
      <div className="chat-input-wrapper">
        <Sparkles size={18} color="var(--purple-primary)" />
        <input
          type="text"
          className="chat-input-field"
          placeholder="Ask about employees, projects, skills, or staffing..."
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="btn-send"
          onClick={() => handleSend()}
          disabled={isLoading || !inputQuestion.trim()}
          title="Send question"
        >
          <Send size={16} />
        </button>
      </div>

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
