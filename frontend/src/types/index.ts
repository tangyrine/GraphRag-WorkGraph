export interface Employee {
  id: string | null;
  name: string;
  role: string | null;
  department: string | null;
  experience: number | null;
  availability?: "Available" | "Assigned" | "Unknown";
  current_project?: string | null;
  skills?: string[];
}

export interface Project {
  id: string | null;
  name: string;
  status: string | null;
}

export interface EmployeeAvailability {
  employee: string;
  role: string | null;
  status: "Available" | "Assigned";
  current_project: string | null;
}

export interface ProjectMatch {
  employee: string;
  role: string | null;
  matching_skills: number;
  total_required: number;
  match_percentage: number;
}

export interface SkillGap {
  skill: string;
  employee_count: number;
  status: "Missing" | "Scarce" | "Available";
}

export interface AssistantTurn {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface AssistantResponse {
  conversation_id: string;
  question: string;
  answer: string;
  retrieval_mode?: string;
  graphrag_results?: any[];
}

export type NavigationPage =
  | "overview"
  | "employees"
  | "projects"
  | "assignments"
  | "add_employee"
  | "add_project"
  | "upload_employee_doc"
  | "upload_project_doc";

export interface ToastMessage {
  id: string;
  type: "success" | "info" | "warning" | "error";
  message: string;
}
