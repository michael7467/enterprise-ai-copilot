import type { ChatRequest, ChatResponse, UploadedFile } from "./types";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------- Chat ----------

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  if (USE_MOCK) return mockChat(req);
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// ---------- Upload ----------

export async function uploadFile(file: File): Promise<UploadedFile> {
  if (USE_MOCK) return mockUpload(file);
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed (${res.status})`);
  return res.json();
}

// ---------- Mocks (remove once the backend is ready) ----------

const mockFiles = new Map<string, UploadedFile>();

async function mockUpload(file: File): Promise<UploadedFile> {
  await new Promise((r) => setTimeout(r, 800));
  const uploaded: UploadedFile = {
    file_id: crypto.randomUUID(),
    filename: file.name,
    size: file.size,
    kind: file.type.startsWith("image/") ? "image" : "document",
  };
  mockFiles.set(uploaded.file_id, uploaded);
  return uploaded;
}

async function mockChat(req: ChatRequest): Promise<ChatResponse> {
  await new Promise((r) => setTimeout(r, 600));
  const file = req.file_id ? mockFiles.get(req.file_id) : undefined;

  if (file?.kind === "image") {
    return {
      answer: `[vision] Mock description of ${file.filename} for: "${req.message}"`,
      route: "vision",
      citations: [{ source: file.filename }],
    };
  }
  if (file) {
    return {
      answer: `[uploaded_file] Mock answer from ${file.filename} to: "${req.message}"`,
      route: "uploaded_file",
      citations: [{ source: file.filename, page: 4 }, { source: file.filename, page: 17 }],
    };
  }
  if (/policy|our|leave|company/i.test(req.message)) {
    return {
      answer: `[knowledge_base] Mock answer to: "${req.message}" (role: ${req.user_role})`,
      route: "knowledge_base",
      citations: [{ source: "HR_Handbook.pdf", page: 12 }],
    };
  }
  return {
    answer: `[direct] Mock answer to: "${req.message}" (role: ${req.user_role})`,
    route: "direct",
    citations: [],
  };
}