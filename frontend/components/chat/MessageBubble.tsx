import type { Confidence, Message, Route } from "@/lib/types";
import AttachmentCard from "@/components/documents/AttachmentCard";

const ROUTE_STYLES: Record<Route, { label: string; className: string }> = {
  direct: { label: "Direct answer", className: "bg-gray-100 text-gray-700" },
  knowledge_base: { label: "Knowledge base", className: "bg-[#E8EEFD] text-[#1E3FAE]" },
  uploaded_file: { label: "Uploaded file", className: "bg-[#FDEBD8] text-[#9A3D00]" },
  vision: { label: "Image", className: "bg-[#E6F4F1] text-[#0F5E52]" },
};

const CONFIDENCE_STYLES: Record<Confidence, { label: string; className: string } | null> = {
  high: null, // no label needed
  low: { label: "Low confidence: check the sources", className: "bg-[#FFF4D6] text-[#7A4B00]" },
  abstained: { label: "Not found in the documents", className: "bg-gray-100 text-gray-700" },
};

interface Props {
  message: Message;
  selectedCitation?: number | null;
  onCitationClick?: (index: number) => void;
}

export default function MessageBubble({ message, selectedCitation, onCitationClick }: Props) {
  if (message.role === "user") {
    return (
      <div className="flex flex-col items-end gap-1.5">
        {message.attachment && <AttachmentCard file={message.attachment} />}
        <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-[#2F5BEA] px-4 py-3 text-[15px] leading-relaxed text-white">
          {message.content}
        </div>
      </div>
    );
  }

  const route = message.route ? ROUTE_STYLES[message.route] : null;
  const confidence = message.confidence ? CONFIDENCE_STYLES[message.confidence] : null;
  // Show cited sources first; uncited ones stay available but de-emphasised.
  const citations = (message.citations ?? []).map((c, i) => ({ ...c, position: i }));

  return (
    <div className="flex max-w-[90%] flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        {route && (
          <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${route.className}`}>
            {route.label}
          </span>
        )}
        {confidence && (
          <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${confidence.className}`}>
            {confidence.label}
          </span>
        )}
      </div>
      <div className="whitespace-pre-line rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3 text-[15px] leading-relaxed text-gray-900">
        {message.content}
      </div>
      {citations.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {citations.map((c) => {
            const selected = selectedCitation === c.position;
            const dim = c.cited === false; // explicitly not cited by the answer
            return (
              <button
                key={c.position}
                type="button"
                onClick={() => onCitationClick?.(c.position)}
                aria-pressed={selected}
                title={dim ? "Given to the model but not cited in the answer" : undefined}
                className={`min-h-8 max-w-full truncate rounded-md border px-2.5 text-[13px] ${
                  selected
                    ? "border-[#1E3FAE] bg-[#EEF2FD] text-[#1E3FAE]"
                    : dim
                    ? "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
                    : "border-[#C7D3F7] bg-white text-[#1E3FAE] hover:bg-[#EEF2FD]"
                }`}
              >
                {c.index ? `[${c.index}] ` : ""}
                {c.source}
                {c.page ? ` · p. ${c.page}` : ""}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
