import { useEffect, useState } from "react";
import { RoomHeader } from "./RoomHeader";
import { ParticipantDrawer } from "./ParticipantDrawer";
import { MessageList } from "./MessageList";
import { MessageComposer } from "./MessageComposer";
import { useRoom } from "../../context/RoomContext";
import "./room.css";

export function RoomPage() {
  const { leaveRoom } = useRoom();
  const [participantsOpen, setParticipantsOpen] = useState(false);

  useEffect(() => {
    const url = new URL(window.location.href);
    url.search = "";
    window.history.replaceState({}, "", url);
  }, []);

  function handleLeave() {
    setParticipantsOpen(false);
    leaveRoom();
  }

  return (
    <div className="room-page">
      <RoomHeader onOpenParticipants={() => setParticipantsOpen(true)} onLeave={handleLeave} />
      <div className="room-body">
        <MessageList />
        <ParticipantDrawer open={participantsOpen} onClose={() => setParticipantsOpen(false)} />
      </div>
      <MessageComposer />
    </div>
  );
}
