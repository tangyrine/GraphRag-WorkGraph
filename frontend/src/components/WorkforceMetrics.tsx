"use client";

import React from "react";
import { Users, Briefcase, Building, CheckCircle2 } from "lucide-react";
import { Employee, Project, EmployeeAvailability } from "../types";

interface WorkforceMetricsProps {
  employees: Employee[];
  projects: Project[];
  availability: EmployeeAvailability[];
}

export default function WorkforceMetrics({
  employees,
  projects,
  availability,
}: WorkforceMetricsProps) {
  const availableCount = availability.filter((a) => a.status === "Available").length;
  const departmentsCount = new Set(
    employees.map((e) => e.department).filter((d): d is string => Boolean(d))
  ).size;

  const metrics = [
    {
      label: "Employees",
      value: employees.length,
      note: "Workforce directory",
      icon: <Users size={16} />,
    },
    {
      label: "Projects",
      value: projects.length,
      note: "Project portfolio",
      icon: <Briefcase size={16} />,
    },
    {
      label: "Departments",
      value: departmentsCount,
      note: "Across the organization",
      icon: <Building size={16} />,
    },
    {
      label: "Available",
      value: availableCount,
      note: "Ready for assignment",
      icon: <CheckCircle2 size={16} />,
    },
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((m, idx) => (
        <div key={idx} className="metric-card">
          <div className="metric-header">
            <span className="metric-label">{m.label}</span>
            <div className="metric-icon-box">{m.icon}</div>
          </div>
          <div>
            <div className="metric-value">{m.value}</div>
            <div className="metric-subtext">{m.note}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
