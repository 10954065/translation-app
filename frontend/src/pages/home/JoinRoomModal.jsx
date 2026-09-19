import { useState } from "react";
import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";
import { LanguageSelect } from "../../components/ui/LanguageSelect";
import { ArrowRightIcon } from "../../components/icons/Icon";
import { useRoom } from "../../context/RoomContext";

const MAX_NAME_LENGTH = 40;

export function JoinRoomModal({ languages, initialCode = "", onClose }) {
  const { joinRoom, state } = useRoom();
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("");
  const [roomCode, setRoomCode] = useState(initialCode);
  const [touched, setTouched] = useState(false);

  const nameError = touched && !name.trim() ? "Please enter your name." : null;
  const languageError = touched && !language ? "Please choose a language." : null;
  const codeError = touched && roomCode.trim().length !== 4 ? "Room codes are 4 characters." : null;

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!name.trim() || !language || roomCode.trim().length !== 4) return;
    joinRoom(name.trim(), language, roomCode.trim().toUpperCase());
  }

  return (
    <Modal title="Join a room" subtitle="Enter the 4-character code you were given." onClose={onClose}>
      <form className="modal-form" onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="join-code" className="field-label">
            Room code
          </label>
          <input
            id="join-code"
            type="text"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value.toUpperCase().slice(0, 4))}
            placeholder="e.g. WDFB"
            maxLength={4}
            className="room-code-input"
            autoComplete="off"
            aria-invalid={Boolean(codeError)}
            aria-describedby={codeError ? "join-code-error" : undefined}
          />
          {codeError && (
            <span className="field-error" id="join-code-error">
              {codeError}
            </span>
          )}
        </div>

        <div className="field">
          <label htmlFor="join-name" className="field-label">
            Your name
          </label>
          <input
            id="join-name"
            type="text"
            value={name}
            maxLength={MAX_NAME_LENGTH}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Daniel"
            autoComplete="name"
            aria-invalid={Boolean(nameError)}
            aria-describedby={nameError ? "join-name-error" : undefined}
          />
          {nameError && (
            <span className="field-error" id="join-name-error">
              {nameError}
            </span>
          )}
        </div>

        <LanguageSelect id="join-language" value={language} onChange={setLanguage} languages={languages} />
        {languageError && <span className="field-error">{languageError}</span>}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="btn-block"
          loading={state.joining}
          icon={<ArrowRightIcon size={18} />}
          iconPosition="right"
        >
          Join room
        </Button>
      </form>
    </Modal>
  );
}
