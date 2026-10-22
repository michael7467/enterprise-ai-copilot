import type { UploadedFile } from "@/lib/types";

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  file: UploadedFile;
  onRemove?: () => void;
}

export default function AttachmentCard({ file, onRemove }: Props) {
  return (
    <div className="flex w-fit max-w-full items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-[13px] text-gray-900">
      <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
        stroke={file.kind === "image" ? "#0F5E52" : "#9A3D00"} strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round">
        {file.kind === "image" ? (
          <>
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="M21 15l-5-5L5 21" />
          </>
        ) : (
          <>
            <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
            <path d="M14 3v5h5" />
          </>
        )}
      </svg>
      <span className="truncate font-semibold">{file.filename}</span>
      <span className="shrink-0 text-gray-600">{formatSize(file.size)}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label={`Remove ${file.filename}`}
          className="ml-1 flex h-6 w-6 shrink-0 items-center justify-center rounded text-gray-600 hover:bg-gray-100"
        >
          <svg aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      )}
    </div>
  );
}