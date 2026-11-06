export type Route = "direct" | "knowledge_base" | "uploaded_file" | "vision";

export type UserRole = "employee" | "hr_manager" | "finance_analyst";

export type Confidence = "high" | "low" | "abstained";

export interface Citation {
  source: string;
  page?: number;
  snippet?: string;
  index?: number;   // the [n] used in the answer
  cited?: boolean;  // did the answer actually cite it?
  doc_id?: string;
}

export interface UploadedFile {
  file_id: string;
  filename: string;
  size: number;
  kind: "document" | "image";
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  route?: Route;
  reason?: string;
  citations?: Citation[];
  attachment?: UploadedFile;
  confidence?: Confidence | null;
  retrieval_score?: number | null;
  latency_ms?: number | null;
}

export interface ChatRequest {
  message: string;
  history: { role: "user" | "assistant"; content: string }[];
  user_role: string;
  file_id?: string;
}

export interface ChatResponse {
  answer: string;
  route: Route;
  reason?: string;
  citations: Citation[];
  confidence?: Confidence | null;
  retrieval_score?: number | null;
  latency_ms?: number | null;
}

export interface Conversation {
  id: string;
  title: string;
}