import pytest
from app.domain.errors.event import EventForbiddenError
from app.domain.errors.session import SessionConflictError
pytestmark = pytest.mark.anyio


async def test_other_user_cannot_create_session(session_context, session_data):
    service, repository, _, _, transaction = session_context
    with pytest.raises(EventForbiddenError):
        await service.create_session(10, session_data, 11)
    repository.add.assert_not_awaited()
    transaction.rollback.assert_awaited_once()


async def test_update_cannot_reduce_capacity_below_registrations(
    session_context,
    session_data
):
    service, repository, _, _, transaction = session_context
    repository.count_registrations.return_value = 3
    with pytest.raises(SessionConflictError):
        await service.update_session(10, 20, session_data, 9)
    repository.update.assert_not_awaited()
    transaction.rollback.assert_awaited_once()


async def test_my_sessions_use_current_user_filter(session_context):
    service, repository, _, _, _ = session_context
    repository.list_sessions.return_value = ([], 0)
    await service.list_registered_sessions(11, page=1, items_per_page=10)
    assert repository.list_sessions.call_args.kwargs[
        'registered_user_id'
    ] == 11
