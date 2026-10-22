import type { Message, Route } from "@/lib/types";

const ROUTE_STYLES: Record<Route, { label: string; className: string }> = {
  direct: { label: "Direct answer", className: "bg-gray-100 text-gray-700" },
  knowledge_base: { label: "Knowledge base", className: "bg-[#E8EEFD] text-[#1E3FAE]" },
  uploaded_file: { label: "Uploaded file", className: "bg-[#FDEBD8] text-[#9A3D00]" },
  vision: { label: "Image", className: "bg-[#E6F4F1] text-[#0F5E52]" },
};

export default function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-[#2F5BEA] px-4 py-3 text-[15px] leading-relaxed text-white">
          {message.content}
        </div>
      </div>
    );
  }

  const route = message.route ? ROUTE_STYLES[message.route] : null;

  return (
    <div className="flex max-w-[90%] flex-col gap-2">
      {route && (
        <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${route.className}`}>
          {route.label}
        </span>
      )}
      <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3 text-[15px] leading-relaxed text-gray-900">
        {message.content}
      </div>
      {message.citations && message.citations.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {message.citations.map((c, i) => (
            <button
              key={i}
              type="button"
              className="min-h-8 rounded-md border border-[#C7D3F7] bg-white px-2.5 text-[13px] text-[#1E3FAE] hover:bg-[#EEF2FD]"
            >
              {c.source}{c.page ? ` · p. ${c.page}` : ""}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}