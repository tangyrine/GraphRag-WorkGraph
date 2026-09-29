"use client";

import React, { useState } from "react";
import { UserCheck, UserMinus, Briefcase, User, Check, Loader2 } from "lucide-react";
import { Project, EmployeeAvailability } from "../types";
import { assignEmployee, unassignEmployee } from "../lib/api";

interface AssignmentsViewProps {
  projects: Project[];
  availability: EmployeeAvailability[];
  onRefreshData: () => Promise<void>;
  onSuccess: (msg: string) => void;
  onError: (msg: string) => void;
}

export default function AssignmentsView({
  projects,
  availability,
  onRefreshData,
  onSuccess,
  onError,
}: AssignmentsViewProps) {
  const availableEmployees = availability.filter((a) => a.status === "Available");
  const assignedEmployees = availability.filter((a) => a.status === "Assigned");

  const [selectedEmp, setSelectedEmp] = useState<string>(
    availableEmployees[0]?.employee || ""
  );
  const [selectedProj, setSelectedProj] = useState<string>(
    projects[0]?.name || ""
  );
  const [isAssigning, setIsAssigning] = useState(false);
  const [unassigningName, setUnassigningName] = useState<string | null>(null);

  const handleAssign = async () => {
    if (!selectedEmp || !selectedProj) {
      onError("Please select both an employee and a project.");
      return;
    }

    setIsAssigning(true);
    try {
      const res = await assignEmployee(selectedEmp, selectedProj);
      if (res.success) {
        onSuccess(res.message || `${selectedEmp} assigned to ${selectedProj}`);
        await onRefreshData();
      } else {
        onError(res.message || "Failed to assign employee");
      }
    } catch (err: any) {
      onError(err.message || "Unable to assign employee");
    } finally {
      setIsAssigning(false);
    }
  };

  const handleUnassign = async (employeeName: string) => {
    setUnassigningName(employeeName);
    try {
      const res = await unassignEmployee(employeeName);
      if (res.success) {
        onSuccess(`${employeeName} has been unassigned and is now Available.`);
        await onRefreshData();
      } else {
        onError(res.message || "Failed to unassign employee");
      }
    } catch (err: any) {
      onError(err.message || "Unable to unassign employee");
    } finally {
      setUnassigningName(null);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "22px" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 800, color: "#000000", letterSpacing: "-0.6px" }}>
          Assign Employee to Project
        </h2>
        <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
          Assignments update the Neo4j graph directly. Availability shown is refreshed in real time.
        </p>
      </div>

      {/* New Assignment Box */}
      <div className="nb-card">
        <h3 style={{ fontSize: "16px", fontWeight: 800, color: "#000000", marginBottom: "14px" }}>
          New Assignment
        </h3>

        {availableEmployees.length > 0 && projects.length > 0 ? (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr)) 130px",
              gap: "14px",
              alignItems: "end",
            }}
          >
            <div>
              <label className="form-label">Available Employee</label>
              <select
                className="form-select"
                value={selectedEmp}
                onChange={(e) => setSelectedEmp(e.target.value)}
              >
                {availableEmployees.map((emp) => (
                  <option key={emp.employee} value={emp.employee}>
                    {emp.employee} {emp.role ? `(${emp.role})` : ""}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="form-label">Target Project</label>
              <select
                className="form-select"
                value={selectedProj}
                onChange={(e) => setSelectedProj(e.target.value)}
              >
                {projects.map((proj) => (
                  <option key={proj.id || proj.name} value={proj.name}>
                    {proj.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="nb-btn nb-btn-primary"
              style={{ height: "42px", justifyContent: "center" }}
              onClick={handleAssign}
              disabled={isAssigning}
            >
              {isAssigning ? (
                <Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} />
              ) : (
                <>
                  <UserCheck size={16} />
                  <span>Assign</span>
                </>
              )}
            </button>
          </div>
        ) : (
          <div style={{ color: "var(--text-muted)", fontSize: "13px", padding: "12px 0" }}>
            {availableEmployees.length === 0
              ? "All employees are currently assigned to projects."
              : "No projects are currently registered."}
          </div>
        )}
      </div>

      {/* Current Assignments List */}
      <div className="nb-card" style={{ marginTop: "24px" }}>
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
              Current Active Assignments
            </h3>
            <p style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
              Staff members currently committed to client and internal projects
            </p>
          </div>
          <span className="status-badge assigned">{assignedEmployees.length} Assigned</span>
        </div>

        {assignedEmployees.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {assignedEmployees.map((emp) => (
              <div
                key={emp.employee}
                style={{
                  background: "#ffffff",
                  border: "1.5px solid var(--border-dark)",
                  borderRadius: "8px",
                  padding: "14px 18px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  boxShadow: "2px 2px 0px #000000",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "8px",
                      background: "var(--purple-light)",
                      border: "1.5px solid var(--border-dark)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 800,
                      color: "var(--purple-text)",
                    }}
                  >
                    {emp.employee.charAt(0)}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: "14px", color: "#000000" }}>
                      {emp.employee}
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                      {emp.role || "Team Member"}
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                      Assigned To
                    </div>
                    <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--purple-text)", display: "flex", alignItems: "center", gap: "5px" }}>
                      <Briefcase size={13} color="var(--purple-primary)" />
                      {emp.current_project}
                    </div>
                  </div>

                  <button
                    className="nb-btn nb-btn-danger"
                    style={{ padding: "6px 12px", fontSize: "12px" }}
                    onClick={() => handleUnassign(emp.employee)}
                    disabled={unassigningName === emp.employee}
                  >
                    {unassigningName === emp.employee ? (
                      <Loader2 size={13} style={{ animation: "spin 1s linear infinite" }} />
                    ) : (
                      <>
                        <UserMinus size={13} />
                        <span>Unassign</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: "32px", textAlign: "center", color: "var(--text-muted)", fontSize: "13px" }}>
            No employees are currently assigned to projects. All staff are available.
          </div>
        )}
      </div>
    </div>
  );
}
