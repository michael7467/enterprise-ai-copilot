"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import SourcesPanel from "@/components/documents/SourcesPanel";
import type { Conversation, Message, UserRole } from "@/lib/types";

function makeTitle(text: string) {
  return text.length > 40 ? text.slice(0, 40).trimEnd() + "…" : text;
}

export default function AppShell() {
  const [role, setRole] = useState<UserRole>("employee");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [chatKey, setChatKey] = useState(0);
  const [sourceMsg, setSourceMsg] = useState<Message | null>(null);
  const [sourceIndex, setSourceIndex] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function resetChat() {
    setChatKey((k) => k + 1);
    setSourceMsg(null);
    setSidebarOpen(false);
  }

  function handleNewChat() {
    setActiveId(null);
    resetChat();
  }

  function handleSelect(id: string) {
    setActiveId(id);
    resetChat();
  }

  function handleFirstMessage(text: string) {
    const id = crypto.randomUUID();
    setConversations((cs) => [{ id, title: makeTitle(text) }, ...cs]);
    setActiveId(id);
  }

  const activeTitle = conversations.find((c) => c.id === activeId)?.title ?? "New chat";

  return (
    <div className="flex h-dvh bg-gray-50">
      {/* Backdrop behind the mobile sidebar */}
      {sidebarOpen && (
        <div
          aria-hidden="true"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-gray-900/40 md:hidden"
        />
      )}

      <Sidebar
        conversations={conversations}
        activeId={activeId}
        role={role}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSelect={handleSelect}
        onNewChat={handleNewChat}
        onRoleChange={setRole}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        {/* Top bar, phone and tablet only */}
        <header className="flex items-center gap-2 border-b border-gray-200 bg-white px-2 py-1.5 md:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
            className="flex h-11 w-11 items-center justify-center rounded-lg text-gray-700 hover:bg-gray-100"
          >
            <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span className="truncate text-[15px] font-semibold text-gray-900">{activeTitle}</span>
        </header>

        <div className="min-h-0 flex-1">
          <ChatWindow
            key={chatKey}
            userRole={role}
            onFirstMessage={handleFirstMessage}
            onSelectSource={(m, i) => {
              setSourceMsg(m);
              setSourceIndex(i);
            }}
          />
        </div>
      </main>

      {/* Backdrop behind the mobile sources drawer */}
      {sourceMsg && (
        <div
          aria-hidden="true"
          onClick={() => setSourceMsg(null)}
          className="fixed inset-0 z-30 bg-gray-900/40 lg:hidden"
        />
      )}

      <SourcesPanel
        message={sourceMsg}
        selectedIndex={sourceIndex}
        onSelect={setSourceIndex}
        onClose={() => setSourceMsg(null)}
      />
    </div>
  );
}