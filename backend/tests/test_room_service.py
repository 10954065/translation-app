import pytest

from app.services.room_service import RoomFullError, RoomNotFoundError, RoomService


@pytest.fixture()
def service():
    return RoomService(max_participants=3, code_length=4)


def test_create_room_generates_four_char_uppercase_code(service):
    room = service.create_room()
    assert len(room.code) == 4
    assert room.code == room.code.upper()


def test_create_room_generates_unique_codes(service):
    codes = {service.create_room().code for _ in range(20)}
    assert len(codes) == 20


def test_get_room_raises_for_unknown_code(service):
    with pytest.raises(RoomNotFoundError):
        service.get_room("ZZZZ")


def test_add_participant_joins_existing_room(service):
    room = service.create_room()
    room, participant = service.add_participant(room.code, "sid-1", "Seyram", "en")
    assert participant.name == "Seyram"
    assert "sid-1" in room.participants


def test_add_participant_raises_for_unknown_room(service):
    with pytest.raises(RoomNotFoundError):
        service.add_participant("ZZZZ", "sid-1", "Seyram", "en")


def test_add_participant_raises_when_room_full(service):
    room = service.create_room()
    service.add_participant(room.code, "sid-1", "A", "en")
    service.add_participant(room.code, "sid-2", "B", "en")
    service.add_participant(room.code, "sid-3", "C", "en")
    with pytest.raises(RoomFullError):
        service.add_participant(room.code, "sid-4", "D", "en")


def test_remove_participant_deletes_room_when_empty(service):
    room = service.create_room()
    service.add_participant(room.code, "sid-1", "Seyram", "en")

    remaining_room, participant = service.remove_participant(room.code, "sid-1")

    assert remaining_room is None
    assert participant.name == "Seyram"
    assert service.room_exists(room.code) is False


def test_remove_participant_keeps_room_when_others_remain(service):
    room = service.create_room()
    service.add_participant(room.code, "sid-1", "Seyram", "en")
    service.add_participant(room.code, "sid-2", "Daniel", "de")

    remaining_room, participant = service.remove_participant(room.code, "sid-1")

    assert remaining_room is not None
    assert "sid-2" in remaining_room.participants
    assert participant.name == "Seyram"


def test_remove_participant_from_nonexistent_room_is_safe(service):
    room, participant = service.remove_participant("ZZZZ", "sid-1")
    assert room is None
    assert participant is None


def test_find_room_for_sid(service):
    room = service.create_room()
    service.add_participant(room.code, "sid-1", "Seyram", "en")

    found = service.find_room_for_sid("sid-1")

    assert found is not None
    assert found.code == room.code


def test_find_room_for_sid_returns_none_when_not_found(service):
    assert service.find_room_for_sid("no-such-sid") is None


def test_rooms_are_isolated_from_each_other(service):
    room_a = service.create_room()
    room_b = service.create_room()
    service.add_participant(room_a.code, "sid-1", "A", "en")
    service.add_participant(room_b.code, "sid-2", "B", "fr")

    assert "sid-2" not in room_a.participants
    assert "sid-1" not in room_b.participants
