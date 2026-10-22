"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import type { Conversation, UserRole } from "@/lib/types";

function makeTitle(text: string) {
  return text.length > 40 ? text.slice(0, 40).trimEnd() + "…" : text;
}

export default function AppShell() {
  const [role, setRole] = useState<UserRole>("employee");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [chatKey, setChatKey] = useState(0);

  function handleNewChat() {
    setActiveId(null);
    setChatKey((k) => k + 1);
  }

  function handleSelect(id: string) {
    setActiveId(id);
    setChatKey((k) => k + 1);
  }

  function handleFirstMessage(text: string) {
    const id = crypto.randomUUID();
    setConversations((cs) => [{ id, title: makeTitle(text) }, ...cs]);
    setActiveId(id);
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        role={role}
        onSelect={handleSelect}
        onNewChat={handleNewChat}
        onRoleChange={setRole}
      />
      <main className="min-w-0 flex-1">
        <ChatWindow key={chatKey} userRole={role} onFirstMessage={handleFirstMessage} />
      </main>
    </div>
  );
}