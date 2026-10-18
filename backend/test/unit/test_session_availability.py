import pytest


@pytest.mark.parametrize(
    'capacity,count,available',
    [(30, 0, 30), (30, 12, 18), (1, 1, 0)]
)
def test_available_capacity_uses_current_occupancy(
    make_session,
    capacity,
    count,
    available
):
    session = make_session(capacity=capacity, registered_count=count)
    assert session.capacity == capacity
    assert session.registered_count == count
    assert session.available_capacity == available
