from sqlmodel import Field, SQLModel


class Status(SQLModel, table=True):
    __tablename__ = "status"

    status_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str | None = None
