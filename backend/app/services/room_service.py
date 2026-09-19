"""In-memory room lifecycle management.

Rooms, participants, and messages live only in process memory for the
lifetime of the room. Per the project's privacy requirement, all state for a
room is deleted the moment its last participant leaves - nothing is
persisted to disk or a database.
"""

from __future__ import annotations

import logging
import threading

from app.models.room import Message, Participant, Room
from app.utils.room_code import generate_room_code

logger = logging.getLogger(__name__)


class RoomNotFoundError(Exception):
    pass


class RoomFullError(Exception):
    pass


class RoomService:
    def __init__(self, max_participants: int = 30, code_length: int = 4):
        self._rooms: dict[str, Room] = {}
        self._lock = threading.Lock()
        self.max_participants = max_participants
        self.code_length = code_length

    # -- lifecycle -----------------------------------------------------

    def create_room(self) -> Room:
        with self._lock:
            code = self._generate_unique_code()
            room = Room(code=code)
            self._rooms[code] = room
            logger.info("Room created: %s", code)
            return room

    def get_room(self, code: str) -> Room:
        with self._lock:
            room = self._rooms.get(code)
        if room is None:
            raise RoomNotFoundError("Room not found or has already closed.")
        return room

    def room_exists(self, code: str) -> bool:
        with self._lock:
            return code in self._rooms

    def add_participant(self, code: str, sid: str, name: str, language: str) -> tuple[Room, Participant]:
        with self._lock:
            room = self._rooms.get(code)
            if room is None:
                raise RoomNotFoundError("Room not found or has already closed.")
            if len(room.participants) >= self.max_participants:
                raise RoomFullError("This room is full.")
            participant = Participant(sid=sid, name=name, language=language)
            room.participants[sid] = participant
            logger.info("Participant %s joined room %s", sid, code)
            return room, participant

    def remove_participant(self, code: str, sid: str) -> tuple[Room | None, Participant | None]:
        """Remove a participant. Deletes the room entirely if it becomes empty.

        Returns (room_or_none, removed_participant_or_none). `room` is None
        when the room was cleaned up as a result of this removal.
        """
        with self._lock:
            room = self._rooms.get(code)
            if room is None:
                return None, None
            participant = room.participants.pop(sid, None)
            if room.is_empty():
                self._rooms.pop(code, None)
                logger.info("Room %s emptied and cleaned up", code)
                return None, participant
            return room, participant

    def find_room_for_sid(self, sid: str) -> Room | None:
        with self._lock:
            for room in self._rooms.values():
                if sid in room.participants:
                    return room
        return None

    def record_message(self, code: str) -> None:
        with self._lock:
            room = self._rooms.get(code)
            if room is not None:
                room.message_count += 1

    def set_pdf_document(self, code: str, document: dict | None) -> None:
        with self._lock:
            room = self._rooms.get(code)
            if room is not None:
                room.pdf_document = document

    def room_count(self) -> int:
        with self._lock:
            return len(self._rooms)

    # -- internal --------------------------------------------------------

    def _generate_unique_code(self) -> str:
        for _ in range(50):
            code = generate_room_code(self.code_length)
            if code not in self._rooms:
                return code
        raise RuntimeError("Could not generate a unique room code")


def build_message(sender: Participant, text: str, source_language: str) -> Message:
    return Message(
        sender_id=sender.sid,
        sender_name=sender.name,
        original_text=text,
        source_language=source_language,
    )
