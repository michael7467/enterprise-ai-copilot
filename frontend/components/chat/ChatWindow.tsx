"use client";

import { useRef, useState } from "react";
import { sendChat, uploadFile } from "@/lib/api";
import type { Message, UploadedFile } from "@/lib/types";
import MessageBubble from "./MessageBubble";
import AttachmentCard from "@/components/documents/AttachmentCard";

const ACCEPTED = ".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.webp";
const MAX_SIZE_MB = 20;

interface ChatWindowProps {
  userRole: string;
  onFirstMessage?: (text: string) => void;
}

export default function ChatWindow({ userRole, onFirstMessage }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [attachment, setAttachment] = useState<UploadedFile | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow picking the same file again
    if (!file) return;
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setUploadError(`File is larger than ${MAX_SIZE_MB} MB.`);
      return;
    }
    setUploadError(null);
    setUploading(true);
    try {
      setAttachment(await uploadFile(file));
    } catch (err) {
      setUploadError((err as Error).message);
    } finally {
      setUploading(false);
    }
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || loading || uploading) return;
    if (messages.length === 0) onFirstMessage?.(text);

    const userMsg: Message = { role: "user", content: text, attachment: attachment ?? undefined };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    const fileId = attachment?.file_id;
    setAttachment(null);
    setLoading(true);
    try {
      const res = await sendChat({
        message: text,
        history: messages,
        user_role: userRole,
        file_id: fileId,
      });
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

      {(attachment || uploading || uploadError) && (
        <div className="pb-2">
          {uploading && <p className="text-sm text-gray-600">Uploading…</p>}
          {uploadError && <p className="text-sm text-red-700">{uploadError}</p>}
          {attachment && <AttachmentCard file={attachment} onRemove={() => setAttachment(null)} />}
        </div>
      )}

      <div className="flex items-end gap-2 rounded-2xl border border-gray-300 bg-white p-2">
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED}
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          aria-label="Attach file"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50"
        >
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 11l-9 9a5 5 0 0 1-7-7l9-9a3.5 3.5 0 0 1 5 5l-9 9a2 2 0 0 1-3-3l8-8" />
          </svg>
        </button>
        <label htmlFor="ask" className="sr-only">Message</label>
        <input
          id="ask"
          className="min-h-11 flex-1 bg-transparent px-2 text-[15px] outline-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={attachment ? `Ask about ${attachment.filename}…` : "Ask a question, or attach a document…"}
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={loading || uploading}
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