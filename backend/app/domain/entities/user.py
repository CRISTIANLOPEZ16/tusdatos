from datetime import datetime, timezone


class User:
    def __init__(
        self,
        *,
        email: str,
        password_hash: str,
        user_id: int | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.email = email
        self.password_hash = password_hash
        self.user_id = user_id
        self.created_at = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc)
        )