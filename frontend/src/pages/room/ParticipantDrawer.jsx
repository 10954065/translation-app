import { Avatar } from "../../components/ui/Avatar";
import { CloseIcon, UsersIcon } from "../../components/icons/Icon";
import { useLanguages } from "../../hooks/useLanguages";
import { languageName } from "../../lib/languages";
import { useRoom } from "../../context/RoomContext";

export function ParticipantDrawer({ open, onClose }) {
  const { state } = useRoom();
  const { languages } = useLanguages();
  const room = state.room;

  return (
    <>
      {open && <div className="drawer-backdrop" onClick={onClose} aria-hidden="true" />}
      <aside className={`participant-drawer ${open ? "participant-drawer--open" : ""}`} aria-label="Participants">
        <div className="drawer-header">
          <h2>
            <UsersIcon size={16} /> Online ({room.participants.length})
          </h2>
          <button type="button" className="icon-btn drawer-close" onClick={onClose} aria-label="Close participants">
            <CloseIcon size={16} />
          </button>
        </div>

        {room.participants.length === 0 ? (
          <p className="drawer-empty">No other participants yet.</p>
        ) : (
          <ul className="participant-list">
            {room.participants.map((p) => (
              <li key={p.id} className="participant-row">
                <Avatar name={p.name} size={34} />
                <div>
                  <span className="participant-name">
                    {p.name}
                    {p.id === room.you.id ? " (you)" : ""}
                  </span>
                  <span className="participant-lang">{languageName(p.language, languages)}</span>
                </div>
                <span className="online-dot" aria-hidden="true" />
              </li>
            ))}
          </ul>
        )}
      </aside>
    </>
  );
}
