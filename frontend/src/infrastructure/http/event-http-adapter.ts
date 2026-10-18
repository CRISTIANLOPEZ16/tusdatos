import type { EventPort } from '../../application/ports/event-port';
import { AppError } from '../../domain/errors';
import type { HttpGet } from './http-client';
import { eventPageSchema } from './schemas';

export function makeEventHttpAdapter(get: HttpGet): EventPort {
  return {
    async list(params, signal) {
      const query = new URLSearchParams({
        page: String(params.page),
        items_per_page: String(params.items_per_page),
      });
      if (params.name?.trim()) query.set('name', params.name.trim());
      const parsed = eventPageSchema.safeParse(await get(`/events?${query}`, signal));
      if (!parsed.success) throw new AppError('La API devolvió datos de eventos inesperados.');
      return parsed.data;
    },
  };
}
