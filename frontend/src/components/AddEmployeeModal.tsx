"use client";

import React, { useState } from "react";
import { UserPlus, X, Check, AlertCircle } from "lucide-react";

interface AddEmployeeModalProps {
  onClose: () => void;
  onSuccess: (msg: string) => void;
}

export default function AddEmployeeModal({ onClose, onSuccess }: AddEmployeeModalProps) {
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [department, setDepartment] = useState("Engineering");
  const [experience, setExperience] = useState(3);
  const [skills, setSkills] = useState("");
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
            <UserPlus size={18} color="var(--purple-primary)" />
            <span className="modal-title">Add Employee</span>
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
            <strong>Backend Integration Notice:</strong> Direct employee creation via HTTP endpoint is pending in the FastAPI backend. You can fill and test this intake form; records will sync to the Neo4j graph once the endpoint is enabled.
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
              <h3 style={{ fontSize: "16px", fontWeight: 800 }}>Employee Record Prepared</h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "6px" }}>
                Candidate <strong>{name}</strong> ({role} - {department}) is queued for graph ingestion.
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
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Samantha Vance"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. AI Engineer"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Department</label>
                  <select
                    className="form-select"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                  >
                    <option value="Engineering">Engineering</option>
                    <option value="AI">AI</option>
                    <option value="Data">Data</option>
                    <option value="Design">Design</option>
                    <option value="Product">Product</option>
                    <option value="Security">Security</option>
                  </select>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "120px 1fr", gap: "14px" }}>
                <div className="form-group">
                  <label className="form-label">Experience</label>
                  <input
                    type="number"
                    min={0}
                    max={40}
                    className="form-input"
                    value={experience}
                    onChange={(e) => setExperience(Number(e.target.value))}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Skills (comma-separated)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Python, LangGraph, Neo4j, Docker"
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "20px" }}>
                <button type="button" className="nb-btn" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="nb-btn nb-btn-primary">
                  Add to Workforce
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
