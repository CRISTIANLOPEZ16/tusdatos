import { z } from 'zod';
import { eventPageSchema } from './schemas';
export const eventSchema = eventPageSchema.shape.items.element;
export const sessionSchema = z.object({
  session_id: z.number().int().positive(), event_id: z.number().int().positive(),
  title: z.string(), starts_at: z.string().datetime({ offset: true }),
  ends_at: z.string().datetime({ offset: true }),
  capacity: z.number().int().positive(), registered_count: z.number().int().nonnegative(),
  available_capacity: z.number().int().nonnegative(), speaker_names: z.array(z.string()),
}).refine(s => s.registered_count + s.available_capacity === s.capacity,
  'La disponibilidad no coincide con el aforo.');
export const detailSchema = eventSchema.extend({ sessions: z.array(sessionSchema) });
export const sessionPageSchema = z.object({
  items: z.array(sessionSchema), total: z.number().int().nonnegative(),
  page: z.number().int().positive(), items_per_page: z.number().int().min(1).max(100),
});
export const registrationSchema = z.object({
  event_id: z.number().int().positive(), session_id: z.number().int().positive(),
  user_id: z.number().int().positive(),
});
