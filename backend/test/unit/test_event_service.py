import pytest
pytestmark = pytest.mark.anyio


async def test_empty_event_can_be_deleted(event_context):
    service, repository, _, transaction = event_context
    await service.delete_event(10, 9)
    repository.delete.assert_awaited_once_with(10)
    transaction.commit.assert_awaited_once()
