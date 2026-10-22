"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import type { Conversation, UserRole } from "@/lib/types";

export default function AppShell() {
  const [role, setRole] = useState<UserRole>("employee");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  function handleNewChat() {
    const id = crypto.randomUUID();
    setConversations((cs) => [{ id, title: "New chat" }, ...cs]);
    setActiveId(id);
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        role={role}
        onSelect={setActiveId}
        onNewChat={handleNewChat}
        onRoleChange={setRole}
      />
      <main className="min-w-0 flex-1">
        <ChatWindow key={activeId ?? "none"} userRole={role} />
      </main>
    </div>
  );
}