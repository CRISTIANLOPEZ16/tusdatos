from sqlmodel import Field, SQLModel


class SessionSpeaker(SQLModel, table=True):
    __tablename__ = "session_speakers"

    session_id: int = Field(
        foreign_key="sessions.session_id", primary_key=True,
    )
    speaker_id: int = Field(
        foreign_key="speakers.speaker_id", primary_key=True,
    )
