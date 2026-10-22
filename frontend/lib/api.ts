import type { ChatRequest, ChatResponse } from "./types";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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

async function mockChat(req: ChatRequest): Promise<ChatResponse> {
  await new Promise((r) => setTimeout(r, 600));
  const isCompany = /policy|our|leave|company/i.test(req.message);
  return isCompany
    ? {
        answer: `[knowledge_base] Mock answer to: "${req.message}" (role: ${req.user_role})`,
        route: "knowledge_base",
        citations: [{ source: "HR_Handbook.pdf", page: 12 }],
      }
    : {
        answer: `[direct] Mock answer to: "${req.message}" (role: ${req.user_role})`,
        route: "direct",
        citations: [],
      };
}