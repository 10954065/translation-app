import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Participant:
    sid: str
    name: str
    language: str
    joined_at: float = field(default_factory=time.time)

    def to_public_dict(self) -> dict:
        return {
            "id": self.sid,
            "name": self.name,
            "language": self.language,
        }


@dataclass
class Message:
    sender_id: str
    sender_name: str
    original_text: str
    source_language: str
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class Room:
    code: str
    created_at: float = field(default_factory=time.time)
    participants: dict = field(default_factory=dict)  # sid -> Participant
    message_count: int = 0
    pdf_document: dict | None = None

    def is_empty(self) -> bool:
        return len(self.participants) == 0

    def participant_list(self) -> list[dict]:
        return [p.to_public_dict() for p in self.participants.values()]
