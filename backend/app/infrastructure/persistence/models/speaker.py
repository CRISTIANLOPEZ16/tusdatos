from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Speaker(SQLModel, table=True):
    __tablename__ = "speakers"
    __table_args__ = (
        UniqueConstraint(
            "normalized_name", name="uq_speakers_normalized_name",
        ),
    )

    speaker_id: int | None = Field(default=None, primary_key=True)
    name: str
    normalized_name: str
