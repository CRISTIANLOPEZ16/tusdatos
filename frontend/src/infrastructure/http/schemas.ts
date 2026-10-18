import { z } from 'zod';

export const eventPageSchema = z.object({
  items: z.array(z.object({
    event_id: z.number().int().positive(),
    name: z.string(),
    description: z.string().nullable(),
    address: z.string(),
    starts_at: z.string().datetime({ offset: true }),
    ends_at: z.string().datetime({ offset: true }),
    status: z.enum(['borrador', 'activo', 'cancelado', 'finalizado', 'archivado']),
    created_by: z.number().int().positive(),
    created_at: z.string().datetime({ offset: true }),
  })),
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  items_per_page: z.number().int().min(1).max(100),
});

export const errorSchema = z.object({ detail: z.string() });
