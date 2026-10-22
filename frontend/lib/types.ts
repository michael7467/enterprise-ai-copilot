export type Route = "direct" | "knowledge_base" | "uploaded_file" | "vision";

export type UserRole = "employee" | "hr_manager" | "finance_analyst";

export interface Citation {
  source: string;
  page?: number;
  snippet?: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  route?: Route;
  reason?: string;
  citations?: Citation[];
  attachment?: UploadedFile;
}

export interface ChatResponse {
  answer: string;
  route: Route;
  reason?: string;
  citations: Citation[];
}

export interface ChatRequest {
  message: string;
  history: Message[];
  user_role: string;
  file_id?: string;
}


export interface Conversation {
  id: string;
  title: string;
}

export interface UploadedFile {
  file_id: string;
  filename: string;
  size: number;
  kind: "document" | "image";
}