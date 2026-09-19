import { useRef, useState } from "react";
import { PaperclipIcon, SendIcon } from "../../components/icons/Icon";
import { useRoom } from "../../context/RoomContext";
import { useToast } from "../../context/ToastContext";

const MAX_MESSAGE_LENGTH = 2000;
const MAX_PDF_SIZE_MB = 10;

export function MessageComposer() {
  const { state, sendMessage, uploadPdf } = useRoom();
  const toast = useToast();
  const [text, setText] = useState("");
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const disconnected = state.connectionStatus !== "connected";

  function handleChange(e) {
    setText(e.target.value.slice(0, MAX_MESSAGE_LENGTH));
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || disconnected) return;
    sendMessage(trimmed);
    setText("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf") || file.type !== "application/pdf") {
      toast.error("Only PDF files are supported.");
      return;
    }
    if (file.size > MAX_PDF_SIZE_MB * 1024 * 1024) {
      toast.error(`PDF files must be smaller than ${MAX_PDF_SIZE_MB} MB.`);
      return;
    }
    if (file.size === 0) {
      toast.error("The selected file is empty.");
      return;
    }
    uploadPdf(file);
  }

  return (
    <div className="composer">
      <button
        type="button"
        className="icon-btn composer-attach"
        onClick={() => fileInputRef.current?.click()}
        disabled={disconnected || state.uploadingPdf}
        aria-label="Attach a PDF"
        title="Attach a PDF"
      >
        <PaperclipIcon size={18} />
      </button>
      <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" hidden onChange={handleFileChange} />

      <textarea
        ref={textareaRef}
        className="composer-input"
        placeholder={disconnected ? "Reconnecting…" : "Type a message…"}
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={disconnected}
        rows={1}
        aria-label="Message"
      />

      <button
        type="button"
        className="btn btn-primary composer-send"
        onClick={handleSend}
        disabled={disconnected || !text.trim() || state.sendingMessage}
        aria-label="Send message"
      >
        <SendIcon size={17} />
      </button>
    </div>
  );
}
