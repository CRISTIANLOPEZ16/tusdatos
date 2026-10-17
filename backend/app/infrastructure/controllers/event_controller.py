from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.application.dto.event import EventData
from app.application.ports.event_use_cases import (
    CreateEventUseCase, DeleteEventUseCase, GetEventUseCase,
    ListEventUseCase, UpdateEventUseCase
)
from app.infrastructure.config.dependencies import get_event_service
from app.infrastructure.controllers.http_errors import (
    CurrentUserId, ERROR_RESPONSES, ResourceId,
)
from app.infrastructure.schemas.event_schema import (
    EventDetailsResponse, EventSummaryResponse,
    EventWriteRequest, ListEventParams, ListEventResponse,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.get(
    "", response_model=ListEventResponse,
    summary='Listar eventos públicos',
    description=(
        'Consulta pública sin cuerpo JSON. Incluye eventos activos, '
        'cancelados y finalizados; excluye borradores y archivados. Permite '
        'paginar y buscar por nombre. Ordena por ID ascendente y devuelve '
        'resúmenes sin sesiones. total cuenta los resultados filtrados antes '
        'de paginar. No admite un filtro de estados del cliente. '
    ),
    response_description='Página de eventos visibles',
    responses={422: ERROR_RESPONSES[422]},
)
async def list_events(
    params: Annotated[ListEventParams, Query()],
    use_case: Annotated[ListEventUseCase, Depends(get_event_service)],
) -> ListEventResponse:
    result = await use_case.list_events_available(**params.model_dump())
    return ListEventResponse(
        items=[
            EventSummaryResponse.model_validate(item) for item in result.items
        ],
        total=result.total, page=result.page,
        items_per_page=result.items_per_page,
    )


@router.post(
    "", response_model=EventSummaryResponse, status_code=201,
    summary='Crear evento',
    description=(
        'Requiere Bearer JWT. El creador se obtiene del token. No permite al '
        'mismo usuario repetir nombre y dirección normalizados con las '
        'mismas fechas de inicio y fin; la descripción no diferencia '
        'duplicados. Otro usuario puede crear un evento equivalente. Las '
        'sesiones se crean por separado. '
    ),
    response_description='Evento creado',
    responses={
        401: ERROR_RESPONSES[401],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def create_event(
    body: EventWriteRequest, user_id: CurrentUserId,
    use_case: Annotated[CreateEventUseCase, Depends(get_event_service)],
) -> EventSummaryResponse:
    result = await use_case.create_event(
        EventData(**body.model_dump()), user_id,
    )
    return EventSummaryResponse.model_validate(result)


@router.get(
    "/{event_id}", response_model=EventDetailsResponse,
    summary='Consultar evento y sus sesiones',
    description=(
        'Consulta pública por ID, sin filtro de estado. Incluye las sesiones '
        'ordenadas por inicio e ID, con aforo total, inscritos y cupos '
        'disponibles al consultar. La disponibilidad no reserva un cupo; se '
        'verifica nuevamente al inscribirse. '
    ),
    response_description='Evento con sesiones y disponibilidad',
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]},
)
async def get_event(
    event_id: ResourceId,
    use_case: Annotated[GetEventUseCase, Depends(get_event_service)],
) -> EventDetailsResponse:
    return EventDetailsResponse.model_validate(
        await use_case.get_event_by_event_id(event_id)
    )


@router.put(
    "/{event_id}", response_model=EventSummaryResponse,
    summary='Actualizar evento',
    description=(
        'Solo el creador autenticado puede actualizarlo. PUT requiere todos '
        'los campos obligatorios; omitir description la deja en null. '
        'Conserva el creador y la fecha de creación. El nuevo horario debe '
        'contener todas las sesiones existentes. Aplica la misma regla de '
        'duplicados que la creación. '
    ),
    response_description='Evento actualizado',
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def update_event(
    event_id: ResourceId, body: EventWriteRequest, user_id: CurrentUserId,
    use_case: Annotated[UpdateEventUseCase, Depends(get_event_service)],
) -> EventSummaryResponse:
    result = await use_case.update_event(
        event_id, EventData(**body.model_dump()), user_id,
    )
    return EventSummaryResponse.model_validate(result)


@router.delete(
    "/{event_id}", status_code=204,
    summary='Eliminar evento',
    description=(
        'Solo el creador autenticado puede eliminarlo. Debe eliminar primero '
        'sus sesiones; si existe alguna, devuelve 409. Una eliminación '
        'correcta devuelve 204 sin cuerpo. '
    ),
    response_description='Evento eliminado, sin cuerpo de respuesta',
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def delete_event(
    event_id: ResourceId, user_id: CurrentUserId,
    use_case: Annotated[DeleteEventUseCase, Depends(get_event_service)],
) -> Response:
    await use_case.delete_event(event_id, user_id)
    return Response(status_code=204)
