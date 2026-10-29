"use client";

import type { Conversation, UserRole } from "@/lib/types";

const ROLES: { value: UserRole; label: string }[] = [
  { value: "employee", label: "Employee" },
  { value: "hr_manager", label: "HR manager" },
  { value: "finance_analyst", label: "Finance analyst" },
];

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  role: UserRole;
  open: boolean;
  onClose: () => void;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onRoleChange: (role: UserRole) => void;
}

export default function Sidebar({
  conversations, activeId, role, open, onClose, onSelect, onNewChat, onRoleChange,
}: SidebarProps) {
  return (
    <nav
      aria-label="Conversations"
      className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col gap-5 border-r border-gray-200 bg-white px-4 py-5 transition-transform duration-200 md:static md:z-auto md:w-64 md:shrink-0 md:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      {/* Brand + close (mobile only) */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2F5BEA]">
            <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="white" strokeWidth="2" strokeLinecap="round">
              <path d="M4 6h16M4 12h10M4 18h7" />
            </svg>
          </div>
          <span className="text-base font-bold text-gray-900">JanoAI</span>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close menu"
          className="flex h-11 w-11 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100 md:hidden"
        >
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <button
        type="button"
        onClick={onNewChat}
        className="flex min-h-11 items-center justify-center gap-2 rounded-lg bg-[#2F5BEA] text-sm font-semibold text-white hover:bg-[#2449C4]"
      >
        <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M12 5v14M5 12h14" />
        </svg>
        New chat
      </button>

      <div className="flex min-h-0 flex-col gap-1 overflow-y-auto">
        <div className="px-2 pb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-600">
          Recent
        </div>
        {conversations.length === 0 && (
          <p className="px-2 text-sm text-gray-600">No conversations yet.</p>
        )}
        {conversations.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => onSelect(c.id)}
            aria-current={c.id === activeId ? "page" : undefined}
            className={`min-h-11 truncate rounded-md px-2 text-left text-sm text-gray-900 hover:bg-gray-100 ${
              c.id === activeId ? "bg-[#EEF2FD] font-semibold" : ""
            }`}
          >
            {c.title}
          </button>
        ))}
      </div>

      <div className="mt-auto flex flex-col gap-2 border-t border-gray-200 pt-4">
        <label htmlFor="role" className="text-xs font-semibold text-gray-600">
          Signed in as
        </label>
        <select
          id="role"
          value={role}
          onChange={(e) => onRoleChange(e.target.value as UserRole)}
          className="min-h-11 rounded-lg border border-gray-300 bg-white px-2.5 text-base text-gray-900 md:text-sm"
        >
          {ROLES.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
        <p className="text-xs text-gray-600">Changes which documents can be searched.</p>
      </div>
    </nav>
  );
}