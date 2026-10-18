import type { ListEventParams } from '../../application/ports/event-port';

export function readEventQuery(search: URLSearchParams): ListEventParams {
  const rawPage = search.get('page') ?? '1';
  const page = Number(rawPage);
  return {
    name: search.get('name')?.trim() || undefined,
    page: /^[1-9]\d*$/.test(rawPage) && Number.isSafeInteger(page) ? page : 1,
    items_per_page: 4,
  };
}
