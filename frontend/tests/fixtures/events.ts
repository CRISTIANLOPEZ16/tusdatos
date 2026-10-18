import type { EventPage, EventSummary } from '../../src/domain/event';

export const later: EventSummary = {
  event_id: 1,
  name: 'React para equipos',
  description: null,
  address: 'Calle 100 # 10-20, Bogotá',
  starts_at: '2027-11-20T09:00:00-05:00',
  ends_at: '2027-11-20T11:00:00-05:00',
  status: 'activo',
  created_by: 1,
  created_at: '2026-10-01T12:00:00Z',
};

export const earlier: EventSummary = {
  ...later, event_id: 2, name: 'Python en comunidad',
  starts_at: '2027-11-01T09:00:00-05:00',
  ends_at: '2027-11-01T11:00:00-05:00',
};

export const firstPage: EventPage = {
  items: [later, earlier, { ...later, event_id: 3, name: 'Diseño en comunidad' },
    { ...earlier, event_id: 4, name: 'Ideas para compartir' }], total: 5, page: 1, items_per_page: 4,
};
