import type { Message } from "@/lib/types";

interface Props {
  message: Message | null;
  selectedIndex: number;
  onSelect: (index: number) => void;
  onClose: () => void;
}

export default function SourcesPanel({ message, selectedIndex, onSelect, onClose }: Props) {
  return (
    <aside
      aria-label="Sources"
      className="hidden h-screen w-80 shrink-0 flex-col gap-5 overflow-y-auto border-l border-gray-200 bg-white p-5 lg:flex"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-[15px] font-semibold text-gray-900">Sources for this answer</h2>
        {message && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close sources"
            className="flex h-8 w-8 items-center justify-center rounded text-gray-600 hover:bg-gray-100"
          >
            <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        )}
      </div>

      {!message && (
        <p className="text-sm text-gray-600">
          Click a citation under an answer to see its source here.
        </p>
      )}

      {message?.citations?.map((c, i) => {
        const selected = i === selectedIndex;
        return (
          <button
            key={i}
            type="button"
            onClick={() => onSelect(i)}
            aria-pressed={selected}
            className={`flex flex-col overflow-hidden rounded-lg border text-left ${
              selected ? "border-[#1E3FAE]" : "border-gray-200 hover:border-gray-300"
            }`}
          >
            {selected && (
              <div className="flex justify-center bg-gray-100 p-4">
                <div
                  role="img"
                  aria-label={`Preview of ${c.source}${c.page ? `, page ${c.page}` : ""}`}
                  className="flex h-44 w-32 flex-col gap-1.5 bg-white p-3 shadow-sm"
                >
                  <div className="h-1.5 w-3/4 rounded-sm bg-gray-300" />
                  <div className="h-1 w-full rounded-sm bg-gray-200" />
                  <div className="h-1 w-5/6 rounded-sm bg-gray-200" />
                  <div className="my-1 h-12 rounded-sm border-2 border-[#E8590C] bg-[#FDEBD8]" />
                  <div className="h-1 w-full rounded-sm bg-gray-200" />
                  <div className="h-1 w-2/3 rounded-sm bg-gray-200" />
                </div>
              </div>
            )}
            <div className="flex flex-col gap-1 px-3.5 py-3">
              <span className="truncate text-sm font-semibold text-gray-900">{c.source}</span>
              {c.page && <span className="text-[13px] text-gray-700">Page {c.page}</span>}
              {selected && c.snippet && (
                <span className="text-[13px] leading-relaxed text-gray-600">{c.snippet}</span>
              )}
            </div>
          </button>
        );
      })}

      {message?.route && (
        <div className="mt-auto flex flex-col gap-2 rounded-lg border border-dashed border-gray-300 bg-gray-50 p-3.5 text-[13px]">
          <span className="font-semibold text-gray-900">Why this route</span>
          <div className="grid grid-cols-2 gap-1.5 text-gray-700">
            <span>Route</span>
            <span className="font-semibold">{message.route}</span>
            <span>Router</span>
            <span>mock</span>
          </div>
          {message.reason && <p className="leading-relaxed text-gray-600">{message.reason}</p>}
        </div>
      )}
    </aside>
  );
}