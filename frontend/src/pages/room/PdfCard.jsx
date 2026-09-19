import { AlertIcon, DownloadIcon, FileTextIcon, LoaderIcon } from "../../components/icons/Icon";

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.replace(/\.pdf$/i, "") + "-translated.txt";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function PdfCard({ pdf }) {
  const isBusy = pdf.status === "uploading" || pdf.status === "processing";

  return (
    <div className="pdf-card">
      <div className="pdf-card-icon">
        <FileTextIcon size={20} />
      </div>
      <div className="pdf-card-body">
        <span className="pdf-card-filename">{pdf.filename}</span>
        <span className="pdf-card-shared-by">Shared by {pdf.sharedBy || "someone"}</span>

        {isBusy && (
          <span className="pdf-card-status">
            <LoaderIcon size={14} /> {pdf.status === "uploading" ? "Uploading…" : "Extracting and translating…"}
          </span>
        )}

        {pdf.status === "done" && pdf.hasExtractableText === false && (
          <span className="pdf-card-status pdf-card-status--warn">
            <AlertIcon size={14} /> {pdf.message || "This PDF has no extractable text."}
          </span>
        )}

        {pdf.status === "done" && pdf.hasExtractableText && (
          <>
            {!pdf.ok && (
              <span className="pdf-card-status pdf-card-status--warn">
                <AlertIcon size={14} /> Translation unavailable. Showing original text.
              </span>
            )}
            <p className="pdf-card-preview">{pdf.text.slice(0, 260)}{pdf.text.length > 260 ? "…" : ""}</p>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => downloadText(pdf.filename, pdf.text)}>
              <DownloadIcon size={14} /> <span>Download translated text</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
