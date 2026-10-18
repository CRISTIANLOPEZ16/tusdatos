export type EventStatus = 'borrador' | 'activo' | 'cancelado' | 'finalizado' | 'archivado';

export interface EventSummary {
  event_id: number;
  name: string;
  description: string | null;
  address: string;
  starts_at: string;
  ends_at: string;
  status: EventStatus;
  created_by: number;
  created_at: string;
}

export interface EventPage {
  items: EventSummary[];
  total: number;
  page: number;
  items_per_page: number;
}
