from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegisteredUser:
    user_id: int
    email: str
    created_at: datetime
