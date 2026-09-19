import { useState } from "react";
import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";
import { LanguageSelect } from "../../components/ui/LanguageSelect";
import { ArrowRightIcon } from "../../components/icons/Icon";
import { useRoom } from "../../context/RoomContext";

const MAX_NAME_LENGTH = 40;

export function CreateRoomModal({ languages, onClose }) {
  const { createRoom, state } = useRoom();
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("");
  const [touched, setTouched] = useState(false);

  const nameError = touched && !name.trim() ? "Please enter your name." : null;
  const languageError = touched && !language ? "Please choose a language." : null;

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!name.trim() || !language) return;
    createRoom(name.trim(), language);
  }

  return (
    <Modal title="Create a room" subtitle="You'll get a 4-character code to share with others." onClose={onClose}>
      <form className="modal-form" onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="create-name" className="field-label">
            Your name
          </label>
          <input
            id="create-name"
            type="text"
            value={name}
            maxLength={MAX_NAME_LENGTH}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Seyram"
            autoComplete="name"
            aria-invalid={Boolean(nameError)}
            aria-describedby={nameError ? "create-name-error" : undefined}
          />
          {nameError && (
            <span className="field-error" id="create-name-error">
              {nameError}
            </span>
          )}
        </div>

        <LanguageSelect id="create-language" value={language} onChange={setLanguage} languages={languages} />
        {languageError && <span className="field-error">{languageError}</span>}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="btn-block"
          loading={state.creating}
          icon={<ArrowRightIcon size={18} />}
          iconPosition="right"
        >
          Create room
        </Button>
      </form>
    </Modal>
  );
}
