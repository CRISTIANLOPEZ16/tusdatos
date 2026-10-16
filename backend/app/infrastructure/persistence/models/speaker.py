from sqlmodel import Field, SQLModel


class Speaker(SQLModel, table=True):
    __tablename__ = "speakers"

    speaker_id: int | None = Field(default=None, primary_key=True)
    name: str
