from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Paginación mediante número de página y cantidad de resultados."""

    page: int = Field(
        default=1, ge=1, description="Página solicitada; la primera es 1.",
        examples=[1],
    )
    items_per_page: int = Field(
        default=10, ge=1, le=100,
        description="Resultados por página (1 a 100). Por defecto: 10.",
        examples=[10],
    )
