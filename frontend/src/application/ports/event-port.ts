import type { EventPage } from '../../domain/event';

export interface ListEventParams {
  name?: string;
  page: number;
  items_per_page: number;
}

export interface EventPort {
  list(params: ListEventParams, signal?: AbortSignal): Promise<EventPage>;
}
