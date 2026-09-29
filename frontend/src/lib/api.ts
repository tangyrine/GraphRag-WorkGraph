import {
  Employee,
  Project,
  EmployeeAvailability,
  ProjectMatch,
  SkillGap,
  AssistantResponse,
  AssistantTurn,
} from "../types";

const API_BASE = "/api/backend";

export async function fetchEmployees(): Promise<Employee[]> {
  const res = await fetch(`${API_BASE}/employees`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch employees: ${res.statusText}`);
  return res.json();
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch projects: ${res.statusText}`);
  return res.json();
}

export async function fetchAvailability(): Promise<EmployeeAvailability[]> {
  const res = await fetch(`${API_BASE}/employees/availability`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch availability: ${res.statusText}`);
  return res.json();
}

export async function fetchProjectMatch(projectName: string): Promise<ProjectMatch[]> {
  const encoded = encodeURIComponent(projectName);
  const res = await fetch(`${API_BASE}/projects/${encoded}/match`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to match project: ${res.statusText}`);
  return res.json();
}

export async function fetchSkillGaps(projectName: string): Promise<SkillGap[]> {
  const encoded = encodeURIComponent(projectName);
  const res = await fetch(`${API_BASE}/projects/${encoded}/skill-gaps`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch skill gaps: ${res.statusText}`);
  return res.json();
}

export async function assignEmployee(
  employeeName: string,
  projectName: string
): Promise<{ success: boolean; message: string }> {
  const encodedEmp = encodeURIComponent(employeeName);
  const encodedProj = encodeURIComponent(projectName);
  const res = await fetch(`${API_BASE}/employees/${encodedEmp}/assign/${encodedProj}`, {
    method: "POST",
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.message || `Assignment request failed (${res.status})`);
  }
  return res.json();
}

export async function unassignEmployee(
  employeeName: string
): Promise<{ success: boolean; message: string; previous_project?: string }> {
  const encodedEmp = encodeURIComponent(employeeName);
  const res = await fetch(`${API_BASE}/employees/${encodedEmp}/unassign`, {
    method: "POST",
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.message || `Unassign request failed (${res.status})`);
  }
  return res.json();
}

export async function askAssistant(
  question: string,
  conversationId?: string,
  history: AssistantTurn[] = []
): Promise<AssistantResponse> {
  const res = await fetch(`${API_BASE}/ai/assistant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      conversation_id: conversationId || undefined,
      history: history.slice(-10).map((h) => ({ role: h.role, content: h.content })),
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.message || `Assistant request failed with status ${res.status}`);
  }

  return res.json();
}
