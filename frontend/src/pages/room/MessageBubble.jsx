import { useState } from "react";
import { Avatar } from "../../components/ui/Avatar";
import { AlertIcon, ChevronDownIcon } from "../../components/icons/Icon";
import { useLanguages } from "../../hooks/useLanguages";
import { languageName } from "../../lib/languages";

function formatTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export function MessageBubble({ message }) {
  const [showOriginal, setShowOriginal] = useState(false);
  const { languages } = useLanguages();
  const wasTranslated = message.sourceLanguage !== message.targetLanguage;

  return (
    <div className={`message-row ${message.isOwn ? "message-row--own" : ""}`}>
      {!message.isOwn && <Avatar name={message.senderName} size={32} />}
      <div className="message-bubble">
        {!message.isOwn && <span className="message-sender">{message.senderName}</span>}
        <p className="message-text">{message.translatedText}</p>
        <div className="message-meta">
          <span>{formatTime(message.timestamp)}</span>
          {!message.translationOk && (
            <span className="message-fallback-flag">
              <AlertIcon size={12} /> original shown
            </span>
          )}
          {wasTranslated && (
            <button type="button" className="message-toggle-original" onClick={() => setShowOriginal((v) => !v)}>
              {showOriginal ? "Hide original" : `Translated from ${languageName(message.sourceLanguage, languages)}`}
              <ChevronDownIcon size={12} className={showOriginal ? "chevron-open" : ""} />
            </button>
          )}
        </div>
        {showOriginal && wasTranslated && <p className="message-original">{message.originalText}</p>}
      </div>
    </div>
  );
}
