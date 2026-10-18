import pytest
from app.domain.entities.event_status import EventStatus
from app.domain.errors.session import InvalidSessionError, SessionConflictError


@pytest.mark.parametrize(
    'names',
    [('',), ('  ',), ('Ana', ' ana '), (1,), ('x' * 151,)]
)
def test_session_rejects_invalid_speaker_names(make_session, names):
    with pytest.raises(InvalidSessionError):
        make_session(speaker_names=names)


def test_capacity_cannot_drop_below_existing_registrations(make_session):
    make_session(capacity=2).ensure_capacity_for(2)
    with pytest.raises(SessionConflictError):
        make_session(capacity=1).ensure_capacity_for(2)


def test_registration_closes_exactly_at_session_start(make_session):
    session = make_session()
    with pytest.raises(SessionConflictError):
        session.ensure_can_register(
            registered_count=0,
            already_registered=False,
            event_status=EventStatus.ACTIVE,
            now=session.starts_at
        )


def test_speakers_must_be_available(make_session):
    session = make_session()
    with pytest.raises(SessionConflictError):
        session.ensure_speakers_available(overlap=True)
