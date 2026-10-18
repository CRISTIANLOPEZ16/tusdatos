import type { SessionPort } from '../../application/ports/session-port';
import { AppError } from '../../domain/errors';
import type { HttpClient } from './http-client';
import { registrationSchema, sessionPageSchema, sessionSchema } from './management-schemas';
export function makeSessionHttpAdapter(http: HttpClient): SessionPort {
  return {
    async mine(page, signal) {
      const parsed = sessionPageSchema.safeParse(await http(`/users/me/sessions?page=${page}&items_per_page=5`, { signal }));
      if (!parsed.success) throw new AppError('No pudimos interpretar tus inscripciones.');
      return parsed.data;
    },
    async create(eventId, input) {
      const parsed = sessionSchema.safeParse(await http(`/events/${eventId}/sessions`, { method: 'POST', body: JSON.stringify(input) }));
      if (!parsed.success) throw new AppError('La API devolvió una sesión inesperada. Recarga el evento antes de reintentar.');
      return parsed.data;
    },
    async register(eventId, sessionId) {
      const parsed = registrationSchema.safeParse(await http(`/events/${eventId}/sessions/${sessionId}/registrations`, { method: 'POST' }));
      if (!parsed.success || parsed.data.event_id !== eventId || parsed.data.session_id !== sessionId) {
        throw new AppError('No pudimos confirmar la inscripción. Consulta tus inscripciones antes de reintentar.');
      }
      return parsed.data;
    },
  };
}
