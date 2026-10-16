from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class User:
    email: str
    password_hash: str = field(repr=False)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    user_id: int | None = None
