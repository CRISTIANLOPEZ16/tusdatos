from datetime import datetime, timedelta, timezone

import jwt

from app.application.ports.token_verifier_port import InvalidTokenError


class JWTTokenAdapter:

    def __init__(
        self, secret: str, expire_minutes: int, algorithm: str,
    ) -> None:
        self.secret = secret
        self.expire_minutes = expire_minutes
        self.algorithm = algorithm

    def issue(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                'sub': str(user_id),
                'iat': now,
                'exp': now + timedelta(minutes=self.expire_minutes),
            },
            self.secret,
            algorithm=self.algorithm,
        )

    def get_user_id(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={'require': ['sub', 'iat', 'exp']},
            )
            subject = payload["sub"]
            if (
                not isinstance(subject, str)
                or not subject.isascii()
                or not subject.isdigit()
                or int(subject) <= 0
            ):
                raise jwt.InvalidTokenError("Invalid subject")
            return int(subject)
        except (jwt.InvalidTokenError, ValueError) as exc:
            raise InvalidTokenError("Invalid or expired token") from exc
