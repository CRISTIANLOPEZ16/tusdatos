from typing import Protocol

from app.application.dto.session import (
    ListedSessions, SessionData, SessionDetails, SessionRegistration,
)


class CreateSessionUseCase(Protocol):
    async def create_session(self, event_id: int, data: SessionData,
                             user_id: int) -> SessionDetails: ...


class GetSessionUseCase(Protocol):
    async def get_session(self, event_id: int,
                          session_id: int) -> SessionDetails: ...


class ListSessionsUseCase(Protocol):
    async def list_sessions(self, event_id: int, *, page: int,
                            items_per_page: int) -> ListedSessions: ...


class UpdateSessionUseCase(Protocol):
    async def update_session(self, event_id: int, session_id: int,
                             data: SessionData,
                             user_id: int) -> SessionDetails: ...


class DeleteSessionUseCase(Protocol):
    async def delete_session(self, event_id: int, session_id: int,
                             user_id: int) -> None: ...


class RegisterSessionUseCase(Protocol):
    async def register_to_session(self, event_id: int, session_id: int,
                                  user_id: int) -> SessionRegistration: ...


class ListRegisteredSessionsUseCase(Protocol):
    async def list_registered_sessions(self, user_id: int, *, page: int,
                                       items_per_page: int
                                       ) -> ListedSessions: ...
