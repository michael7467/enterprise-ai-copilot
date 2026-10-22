"use client";

import { useState } from "react";
import { sendChat } from "@/lib/api";
import type { Message } from "@/lib/types";
import MessageBubble from "./MessageBubble";

interface ChatWindowProps {
  userRole: string;
  onFirstMessage?: (text: string) => void;
}

export default function ChatWindow({ userRole, onFirstMessage }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;
    if (messages.length === 0) onFirstMessage?.(text);
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendChat({ message: text, history: messages, user_role: userRole });
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, route: res.route, citations: res.citations },
      ]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${(e as Error).message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col p-6">
      <div className="flex-1 space-y-6 overflow-y-auto pb-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <h1 className="text-2xl font-bold text-gray-900">How can JanoAI help?</h1>
            <p className="mt-2 text-sm text-gray-600">
              Ask about company policies, or attach a document.
            </p>
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && <div className="text-sm text-gray-600">Thinking…</div>}
      </div>

      <div className="flex items-end gap-2 rounded-2xl border border-gray-300 bg-white p-2">
        <label htmlFor="ask" className="sr-only">Message</label>
        <input
          id="ask"
          className="min-h-11 flex-1 bg-transparent px-2 text-[15px] outline-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question…"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={loading}
          className="min-h-11 rounded-lg bg-[#2F5BEA] px-5 text-sm font-semibold text-white hover:bg-[#2449C4] disabled:opacity-50"
        >
          Send
        </button>
      </div>
      <p className="pt-2 text-center text-xs text-gray-600">
        Answers cite their sources. Only documents your role can access are searched.
      </p>
    </div>
  );
}