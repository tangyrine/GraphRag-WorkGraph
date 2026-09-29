"use client";

import React, { useState, useMemo } from "react";
import { Search, UserCheck, ShieldAlert, Briefcase, Filter } from "lucide-react";
import { Employee, EmployeeAvailability } from "../types";

interface EmployeesViewProps {
  employees: Employee[];
  availability: EmployeeAvailability[];
}

export default function EmployeesView({ employees, availability }: EmployeesViewProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDept, setSelectedDept] = useState<string>("All");
  const [selectedStatus, setSelectedStatus] = useState<string>("All");

  const availabilityMap = useMemo(() => {
    const map = new Map<string, EmployeeAvailability>();
    availability.forEach((item) => {
      map.set(item.employee, item);
    });
    return map;
  }, [availability]);

  const departments = useMemo(() => {
    const depts = new Set<string>();
    employees.forEach((e) => {
      if (e.department) depts.add(e.department);
    });
    return ["All", ...Array.from(depts).sort()];
  }, [employees]);

  const enrichedEmployees = useMemo(() => {
    return employees.map((emp) => {
      const avail = availabilityMap.get(emp.name);
      return {
        ...emp,
        status: avail?.status || "Unknown",
        current_project: avail?.current_project || null,
      };
    });
  }, [employees, availabilityMap]);

  const filteredEmployees = useMemo(() => {
    return enrichedEmployees.filter((emp) => {
      const matchesSearch =
        emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (emp.role && emp.role.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (emp.department && emp.department.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesDept = selectedDept === "All" || emp.department === selectedDept;
      const matchesStatus = selectedStatus === "All" || emp.status === selectedStatus;

      return matchesSearch && matchesDept && matchesStatus;
    });
  }, [enrichedEmployees, searchTerm, selectedDept, selectedStatus]);

  return (
    <div>
      <div style={{ marginBottom: "22px" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 800, color: "#000000", letterSpacing: "-0.6px" }}>
          Workforce Directory
        </h2>
        <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
          Browse organizational talent, verified skills, and real-time Neo4j assignment status.
        </p>
      </div>

      {/* Search and Filters Bar */}
      <div
        className="nb-card-flat"
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "14px",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "18px",
        }}
      >
        <div style={{ position: "relative", minWidth: "280px", flex: "1 1 300px" }}>
          <Search
            size={16}
            style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "#64748b" }}
          />
          <input
            type="text"
            placeholder="Search employees by name, role, department..."
            className="form-input"
            style={{ paddingLeft: "36px" }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Availability Filter */}
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
            Status:
          </span>
          {["All", "Available", "Assigned"].map((status) => (
            <button
              key={status}
              className={`pill-btn ${selectedStatus === status ? "active" : ""}`}
              onClick={() => setSelectedStatus(status)}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Department Filter Pills */}
      <div className="filter-pills-bar">
        <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", alignSelf: "center", marginRight: "4px" }}>
          Department:
        </span>
        {departments.map((dept) => (
          <button
            key={dept}
            className={`pill-btn ${selectedDept === dept ? "active" : ""}`}
            onClick={() => setSelectedDept(dept)}
          >
            {dept}
          </button>
        ))}
      </div>

      {/* Directory Table */}
      <div className="nb-table-wrap">
        <table className="nb-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Role</th>
              <th>Department</th>
              <th>Experience</th>
              <th>Status</th>
              <th>Current Assignment</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.length > 0 ? (
              filteredEmployees.map((emp, idx) => (
                <tr key={emp.id || emp.name || idx}>
                  <td style={{ fontWeight: 700, color: "#000000" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <div
                        style={{
                          width: "30px",
                          height: "30px",
                          borderRadius: "6px",
                          background: "#f4f4f5",
                          border: "1.5px solid var(--border-dark)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "12px",
                          fontWeight: 800,
                        }}
                      >
                        {emp.name.charAt(0)}
                      </div>
                      <span>{emp.name}</span>
                    </div>
                  </td>
                  <td style={{ fontWeight: 500 }}>{emp.role || "—"}</td>
                  <td>
                    {emp.department ? (
                      <span
                        style={{
                          background: "#f8fafc",
                          border: "1px solid #cbd5e1",
                          borderRadius: "4px",
                          padding: "2px 8px",
                          fontSize: "11px",
                          fontWeight: 600,
                        }}
                      >
                        {emp.department}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>{emp.experience ? `${emp.experience} yrs` : "—"}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        emp.status === "Available"
                          ? "available"
                          : emp.status === "Assigned"
                          ? "assigned"
                          : "missing"
                      }`}
                    >
                      {emp.status === "Available" && <UserCheck size={11} />}
                      {emp.status}
                    </span>
                  </td>
                  <td>
                    {emp.current_project ? (
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "5px",
                          fontWeight: 600,
                          color: "#1e1b4b",
                        }}
                      >
                        <Briefcase size={12} color="var(--purple-primary)" />
                        {emp.current_project}
                      </span>
                    ) : (
                      <span style={{ color: "#9ca3af" }}>None</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
                  No employees found matching the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: "12px", fontSize: "12px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
        <span>Showing {filteredEmployees.length} of {employees.length} employees</span>
        <span>Backed by live Neo4j database</span>
      </div>
    </div>
  );
}
