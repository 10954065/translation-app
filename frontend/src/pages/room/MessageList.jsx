import { useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import { SystemMessage } from "./SystemMessage";
import { PdfCard } from "./PdfCard";
import { TranslateArrowsIcon } from "../../components/icons/Icon";
import { useRoom } from "../../context/RoomContext";

export function MessageList() {
  const { state } = useRoom();
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [state.messages.length]);

  if (state.messages.length === 0) {
    return (
      <div className="message-list message-list--empty">
        <div className="empty-state">
          <span className="empty-state-icon">
            <TranslateArrowsIcon size={24} />
          </span>
          <p className="empty-state-title">No messages yet</p>
          <p className="empty-state-description">
            Start the conversation by sending a message. Everyone will read it in their own language.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="message-list">
      {state.messages.map((entry) => {
        if (entry.kind === "system") return <SystemMessage key={entry.id} text={entry.text} />;
        if (entry.kind === "pdf") return <PdfCard key={entry.id} pdf={entry} />;
        return <MessageBubble key={entry.id} message={entry} />;
      })}
      <div ref={endRef} />
    </div>
  );
}
