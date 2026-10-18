import type { EventPage } from '../../domain/event';

export interface ListEventParams {
  name?: string;
  page: number;
  items_per_page: number;
}

export interface EventPort {
  list(params: ListEventParams, signal?: AbortSignal): Promise<EventPage>;
}

export interface EventManagementPort {
  detail(id: number, signal?: AbortSignal): Promise<import('../../domain/event').EventDetails>;
  mine(page: number, signal?: AbortSignal): Promise<EventPage>;
  create(input: import('../../domain/event').EventInput): Promise<import('../../domain/event').EventSummary>;
  update(id: number, input: import('../../domain/event').EventInput): Promise<import('../../domain/event').EventSummary>;
}
