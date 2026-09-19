import { useState } from "react";
import { Avatar } from "../../components/ui/Avatar";
import { ConnectionBadge } from "../../components/ui/ConnectionBadge";
import { CopyIcon, CheckIcon, UsersIcon, DoorExitIcon, TranslateArrowsIcon } from "../../components/icons/Icon";
import { useRoom } from "../../context/RoomContext";

export function RoomHeader({ onOpenParticipants, onLeave }) {
  const { state } = useRoom();
  const [copied, setCopied] = useState(false);
  const room = state.room;

  function handleCopy() {
    navigator.clipboard
      ?.writeText(room.code)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
      })
      .catch(() => {});
  }

  const visibleAvatars = room.participants.slice(0, 4);
  const extraCount = room.participants.length - visibleAvatars.length;

  return (
    <header className="room-header">
      <div className="room-header-left">
        <span className="room-brand">
          <TranslateArrowsIcon size={18} />
        </span>
        <button type="button" className="room-code-chip" onClick={handleCopy} aria-label="Copy room code">
          <span>{room.code}</span>
          {copied ? <CheckIcon size={14} /> : <CopyIcon size={14} />}
        </button>
      </div>

      <div className="room-header-right">
        <ConnectionBadge status={state.connectionStatus} />

        <button type="button" className="participant-stack" onClick={onOpenParticipants} aria-label="View participants">
          <span className="avatar-stack">
            {visibleAvatars.map((p) => (
              <Avatar key={p.id} name={p.name} size={28} />
            ))}
          </span>
          <span className="participant-count">
            <UsersIcon size={14} />
            {room.participants.length}
            {extraCount > 0 ? ` +${extraCount}` : ""}
          </span>
        </button>

        <button type="button" className="icon-btn" onClick={onLeave} aria-label="Leave room">
          <DoorExitIcon size={17} />
        </button>
      </div>
    </header>
  );
}
