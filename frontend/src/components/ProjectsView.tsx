"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, CheckCircle, AlertTriangle, UserCheck, Layers, Loader2, BarChart2 } from "lucide-react";
import { Project, ProjectMatch, SkillGap } from "../types";
import { fetchProjectMatch, fetchSkillGaps } from "../lib/api";

interface ProjectsViewProps {
  projects: Project[];
  onError: (msg: string) => void;
}

export default function ProjectsView({ projects, onError }: ProjectsViewProps) {
  const [selectedProjectName, setSelectedProjectName] = useState<string>(
    projects[0]?.name || ""
  );
  const [matches, setMatches] = useState<ProjectMatch[]>([]);
  const [skillGaps, setSkillGaps] = useState<SkillGap[]>([]);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  useEffect(() => {
    if (!selectedProjectName && projects.length > 0) {
      setSelectedProjectName(projects[0].name);
    }
  }, [projects, selectedProjectName]);

  useEffect(() => {
    if (!selectedProjectName) return;

    let isMounted = true;
    setLoadingAnalysis(true);

    Promise.all([
      fetchProjectMatch(selectedProjectName).catch(() => []),
      fetchSkillGaps(selectedProjectName).catch(() => []),
    ])
      .then(([matchData, gapData]) => {
        if (!isMounted) return;
        setMatches(matchData);
        setSkillGaps(gapData);
      })
      .catch((err) => {
        if (!isMounted) return;
        onError(`Failed to analyze project: ${err.message}`);
      })
      .finally(() => {
        if (isMounted) setLoadingAnalysis(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedProjectName, onError]);

  return (
    <div>
      <div style={{ marginBottom: "22px" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 800, color: "#000000", letterSpacing: "-0.6px" }}>
          Project Portfolio
        </h2>
        <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
          Evaluate project staffing requirements, candidate suitability, and organizational skill gaps.
        </p>
      </div>

      {/* Project Selector Bar */}
      <div
        className="nb-card-flat"
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: "14px",
          marginBottom: "24px",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flex: "1 1 300px" }}>
          <label style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px" }}>
            Select Project:
          </label>
          <select
            className="form-select"
            style={{ maxWidth: "340px", fontWeight: 600 }}
            value={selectedProjectName}
            onChange={(e) => setSelectedProjectName(e.target.value)}
          >
            {projects.map((p, idx) => (
              <option key={p.id || p.name || idx} value={p.name}>
                {p.name} {p.status ? `(${p.status})` : ""}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          {selectedProjectName && (
            <span className="status-badge assigned" style={{ padding: "6px 12px", fontSize: "12px" }}>
              <Briefcase size={13} />
              <span>{selectedProjectName}</span>
            </span>
          )}
        </div>
      </div>

      {/* Analysis Grid: Matches + Skill Gaps */}
      {loadingAnalysis ? (
        <div
          className="nb-card"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            padding: "48px",
          }}
        >
          <Loader2 size={24} style={{ animation: "spin 1s linear infinite" }} />
          <span style={{ fontWeight: 600, fontSize: "14px", color: "var(--text-muted)" }}>
            Analyzing candidate matches and skill gaps in graph...
          </span>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "22px" }}>
          {/* Left Column: Recommended Available People */}
          <div className="nb-card">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                paddingBottom: "14px",
                borderBottom: "2px solid var(--border-dark)",
                marginBottom: "16px",
              }}
            >
              <div>
                <h3 style={{ fontSize: "16px", fontWeight: 800, color: "#000000" }}>
                  Recommended Available People
                </h3>
                <p style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                  Unassigned candidates ranked by required skill overlap
                </p>
              </div>
              <span className="status-badge available">{matches.length} Candidates</span>
            </div>

            {matches.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {matches.map((m, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: "#ffffff",
                      border: "1.5px solid var(--border-dark)",
                      borderRadius: "8px",
                      padding: "12px 14px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      boxShadow: "2px 2px 0px #000000",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "13.5px", color: "#000000" }}>
                        {m.employee}
                      </div>
                      <div style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                        {m.role || "Staff"} • {m.matching_skills} of {m.total_required} skills matched
                      </div>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <span
                        style={{
                          display: "inline-block",
                          fontWeight: 800,
                          fontSize: "14px",
                          color: m.match_percentage >= 50 ? "var(--green-primary)" : "var(--purple-primary)",
                          background: m.match_percentage >= 50 ? "var(--green-light)" : "var(--purple-light)",
                          border: "1.5px solid var(--border-dark)",
                          borderRadius: "6px",
                          padding: "3px 8px",
                        }}
                      >
                        {m.match_percentage}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", fontSize: "13px" }}>
                No available unassigned employees currently match this project's requirements.
              </div>
            )}
          </div>

          {/* Right Column: Skill Coverage & Gaps */}
          <div className="nb-card">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                paddingBottom: "14px",
                borderBottom: "2px solid var(--border-dark)",
                marginBottom: "16px",
              }}
            >
              <div>
                <h3 style={{ fontSize: "16px", fontWeight: 800, color: "#000000" }}>
                  Skill Coverage & Gap Analysis
                </h3>
                <p style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                  Required skills mapped against workforce availability
                </p>
              </div>
              <span className="status-badge assigned">{skillGaps.length} Skills</span>
            </div>

            {skillGaps.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {skillGaps.map((gap, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: "#ffffff",
                      border: "1.5px solid var(--border-dark)",
                      borderRadius: "8px",
                      padding: "12px 14px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      boxShadow: "2px 2px 0px #000000",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "13.5px", color: "#000000" }}>
                        {gap.skill}
                      </div>
                      <div style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                        {gap.employee_count} {gap.employee_count === 1 ? "person" : "people"} in organization
                      </div>
                    </div>

                    <div>
                      <span
                        className={`status-badge ${
                          gap.status === "Available"
                            ? "available"
                            : gap.status === "Scarce"
                            ? "scarce"
                            : "missing"
                        }`}
                      >
                        {gap.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", fontSize: "13px" }}>
                No explicit skill requirements found for this project in the graph.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Complete Project Directory Table */}
      <div style={{ marginTop: "32px" }}>
        <h3 style={{ fontSize: "16px", fontWeight: 800, color: "#000000", marginBottom: "12px" }}>
          Full Project Directory
        </h3>
        <div className="nb-table-wrap">
          <table className="nb-table">
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((proj, idx) => (
                <tr key={proj.id || proj.name || idx}>
                  <td style={{ fontWeight: 700, color: "#000000" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <Briefcase size={14} color="var(--purple-primary)" />
                      <span>{proj.name}</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className={`status-badge ${
                        proj.status === "Active"
                          ? "available"
                          : proj.status === "Planning"
                          ? "assigned"
                          : "missing"
                      }`}
                    >
                      {proj.status || "Unknown"}
                    </span>
                  </td>
                  <td>
                    <button
                      className="nb-btn nb-btn-purple-subtle"
                      style={{ padding: "4px 10px", fontSize: "11px" }}
                      onClick={() => setSelectedProjectName(proj.name)}
                    >
                      <BarChart2 size={12} />
                      Inspect Fit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
