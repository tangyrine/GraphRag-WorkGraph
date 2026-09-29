"use client";

import React, { useState } from "react";
import { FolderPlus, X, Check } from "lucide-react";

interface AddProjectModalProps {
  onClose: () => void;
  onSuccess: (msg: string) => void;
}

export default function AddProjectModal({ onClose, onSuccess }: AddProjectModalProps) {
  const [name, setName] = useState("");
  const [status, setStatus] = useState("Planning");
  const [skills, setSkills] = useState("");
  const [description, setDescription] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitted(true);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <FolderPlus size={18} color="var(--purple-primary)" />
            <span className="modal-title">Add Project</span>
          </div>
          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "#64748b" }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="info-banner">
            <strong>Backend Integration Notice:</strong> Project creation via HTTP endpoint is pending in the FastAPI backend. You can fill and validate this project intake form; records will sync to the Neo4j graph once the endpoint is enabled.
          </div>

          {submitted ? (
            <div style={{ textAlign: "center", padding: "24px 12px" }}>
              <div
                style={{
                  width: "48px",
                  height: "48px",
                  background: "var(--green-light)",
                  border: "2px solid var(--border-dark)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 14px",
                  color: "var(--green-primary)",
                }}
              >
                <Check size={24} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 800 }}>Project Record Prepared</h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "6px" }}>
                Project <strong>{name}</strong> (Status: {status}) is ready for graph ingestion.
              </p>
              <button
                className="nb-btn nb-btn-primary"
                style={{ marginTop: "18px" }}
                onClick={onClose}
              >
                Done
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Project Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Enterprise Knowledge Agent"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Initial Status</label>
                <select
                  className="form-select"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                >
                  <option value="Planning">Planning</option>
                  <option value="Active">Active</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Required Skills (comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Python, FastAPI, Neo4j, Cypher"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Project Scope / Summary</label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder="Objectives, deliverables, and domain context..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "20px" }}>
                <button type="button" className="nb-btn" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="nb-btn nb-btn-primary">
                  Create Project
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
