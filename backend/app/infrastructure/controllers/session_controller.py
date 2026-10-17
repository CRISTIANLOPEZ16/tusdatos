from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.application.dto.session import SessionData
from app.application.ports.session_use_cases import (
    CreateSessionUseCase, DeleteSessionUseCase, GetSessionUseCase,
    ListSessionsUseCase, RegisterSessionUseCase, UpdateSessionUseCase,
)
from app.infrastructure.config.dependencies import get_session_service
from app.infrastructure.controllers.http_errors import (
    CurrentUserId, ERROR_RESPONSES, ResourceId,
)
from app.infrastructure.schemas.pagination import PaginationParams
from app.infrastructure.schemas.session_schema import (
    SESSION_RESPONSE_EXAMPLE, ListSessionResponse,
    SessionRegistrationResponse, SessionResponse,
    SessionWriteRequest,
)


router = APIRouter(prefix="/events/{event_id}/sessions", tags=["Sessions"])


@router.get(
    "", response_model=ListSessionResponse,
    summary='Listar sesiones de un evento',
    description=(
        'Consulta pública paginada. El evento debe existir. Ordena las '
        'sesiones por inicio e ID. Cada resultado incluye capacity (aforo '
        'total), registered_count (inscritos) y available_capacity (cupos '
        'libres al consultar). No requiere cuerpo JSON. '
    ),
    response_description='Página de sesiones con disponibilidad',
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]},
)
async def list_sessions(
    event_id: ResourceId, params: Annotated[PaginationParams, Query()],
    use_case: Annotated[ListSessionsUseCase, Depends(get_session_service)],
) -> ListSessionResponse:
    return ListSessionResponse.model_validate(
        await use_case.list_sessions(event_id, **params.model_dump())
    )


@router.post(
    "", response_model=SessionResponse, status_code=201,
    summary='Crear sesión',
    description=(
        'Solo el creador del evento puede crear sesiones. El horario debe '
        'estar dentro del evento. Recibe nombres de ponentes: crea los '
        'nuevos y reutiliza los existentes sin distinguir mayúsculas y '
        'compactando espacios. No permite repetir un ponente ni asignarlo a '
        'horarios superpuestos, incluso entre eventos. La sesión se crea sin '
        'inscritos y con todos sus cupos libres. '
    ),
    response_description='Sesión creada sin inscripciones',
    responses={
        201: {
            "content": {"application/json": {"example": {
                **SESSION_RESPONSE_EXAMPLE,
                "registered_count": 0, "available_capacity": 30,
            }}},
        },
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def create_session(
    event_id: ResourceId, body: SessionWriteRequest, user_id: CurrentUserId,
    use_case: Annotated[CreateSessionUseCase, Depends(get_session_service)],
) -> SessionResponse:
    return SessionResponse.model_validate(await use_case.create_session(
        event_id, SessionData(**body.model_dump()), user_id,
    ))


@router.get(
    "/{session_id}", response_model=SessionResponse,
    summary='Consultar sesión',
    description=(
        'Consulta pública. La sesión debe pertenecer al evento indicado. '
        'Incluye ponentes, aforo total, inscritos y cupos libres al '
        'consultar. Los cupos mostrados no constituyen una reserva. '
    ),
    response_description='Sesión con disponibilidad actual',
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]},
)
async def get_session(
    event_id: ResourceId, session_id: ResourceId,
    use_case: Annotated[GetSessionUseCase, Depends(get_session_service)],
) -> SessionResponse:
    return SessionResponse.model_validate(
        await use_case.get_session(event_id, session_id)
    )


@router.put(
    "/{session_id}", response_model=SessionResponse,
    summary='Actualizar sesión',
    description=(
        'Solo el creador del evento puede actualizarla. PUT requiere todos '
        'los campos obligatorios y reemplaza la lista de ponentes; omitir '
        'speaker_names equivale a enviar []. El aforo no puede ser menor que '
        'los inscritos. Conserva las inscripciones y valida horario dentro '
        'del evento y disponibilidad de los ponentes. '
    ),
    response_description='Sesión actualizada con su ocupación actual',
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def update_session(
    event_id: ResourceId, session_id: ResourceId,
    body: SessionWriteRequest, user_id: CurrentUserId,
    use_case: Annotated[UpdateSessionUseCase, Depends(get_session_service)],
) -> SessionResponse:
    return SessionResponse.model_validate(await use_case.update_session(
        event_id, session_id, SessionData(**body.model_dump()), user_id,
    ))


@router.delete(
    "/{session_id}", status_code=204,
    summary='Eliminar sesión',
    description=(
        'Solo el creador del evento puede eliminarla. Si tiene inscritos, '
        'devuelve 409. Elimina las asociaciones de ponentes de esta sesión, '
        'conservando los ponentes para otras sesiones. Devuelve 204 sin '
        'cuerpo. '
    ),
    response_description='Sesión eliminada, sin cuerpo de respuesta',
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def delete_session(
    event_id: ResourceId, session_id: ResourceId, user_id: CurrentUserId,
    use_case: Annotated[DeleteSessionUseCase, Depends(get_session_service)],
) -> Response:
    await use_case.delete_session(event_id, session_id, user_id)
    return Response(status_code=204)


@router.post(
    "/{session_id}/registrations", status_code=201,
    response_model=SessionRegistrationResponse,
    summary='Inscribirse a una sesión',
    description=(
        'Requiere Bearer JWT y no recibe cuerpo JSON ni user_id. Inscribe al '
        'usuario del token, sin inscripción previa al evento. El evento debe '
        'estar activo y la sesión no debe haber comenzado. Devuelve 409 si '
        'ya está inscrito, no quedan cupos o no se cumplen esas condiciones. '
        'El cupo se verifica al confirmar la inscripción, también ante '
        'solicitudes simultáneas. '
    ),
    response_description='Inscripción confirmada para el usuario autenticado',
    responses={
        401: ERROR_RESPONSES[401],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
    },
)
async def register_to_session(
    event_id: ResourceId, session_id: ResourceId, user_id: CurrentUserId,
    use_case: Annotated[RegisterSessionUseCase, Depends(get_session_service)],
) -> SessionRegistrationResponse:
    return SessionRegistrationResponse.model_validate(
        await use_case.register_to_session(event_id, session_id, user_id)
    )
