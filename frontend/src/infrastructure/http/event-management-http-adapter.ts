import type { EventManagementPort } from '../../application/ports/event-port';
import type { HttpClient } from './http-client';
import { AppError } from '../../domain/errors';
import { detailSchema, eventSchema } from './management-schemas';
import { eventPageSchema } from './schemas';
export function makeEventManagementHttpAdapter(publicHttp: HttpClient, privateHttp: HttpClient): EventManagementPort {
  return {
    async detail(id, signal) {
      const parsed = detailSchema.safeParse(await publicHttp(`/events/${id}`, { signal }));
      if (!parsed.success) throw new AppError('No pudimos interpretar el detalle del evento.');
      return parsed.data;
    },
    async mine(page, signal) {
      const parsed = eventPageSchema.safeParse(await privateHttp(`/users/me/events?page=${page}&items_per_page=6`, { signal }));
      if (!parsed.success) throw new AppError('No pudimos interpretar tus eventos.');
      return parsed.data;
    },
    async create(input) {
      const parsed = eventSchema.safeParse(await privateHttp('/events', { method: 'POST', body: JSON.stringify(input) }));
      if (!parsed.success) throw new AppError('La API devolvió un evento inesperado. Consulta tu dashboard antes de volver a crear.');
      return parsed.data;
    },
    async update(id, input) {
      const parsed = eventSchema.safeParse(await privateHttp(`/events/${id}`, { method: 'PUT', body: JSON.stringify(input) }));
      if (!parsed.success) throw new AppError('La API devolvió un evento inesperado. Recarga el detalle antes de reintentar.');
      return parsed.data;
    },
  };
}
