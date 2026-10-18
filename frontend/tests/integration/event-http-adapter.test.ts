import { describe, expect, it, vi } from 'vitest';
import { getJson } from '../../src/infrastructure/http/http-client';
import { makeEventHttpAdapter } from '../../src/infrastructure/http/event-http-adapter';
import { firstPage } from '../fixtures/events';

describe('listado HTTP', () => {
  it('envía el filtro, la paginación y la señal al endpoint de eventos', async () => {
    const fetchMock = vi.fn().mockResolvedValue(Response.json(firstPage));
    vi.stubGlobal('fetch', fetchMock);
    const signal = new AbortController().signal;
    const result = await makeEventHttpAdapter(getJson).list({
      name: 'React & UX', page: 1, items_per_page: 4,
    }, signal);
    expect(result.items.map((event) => event.event_id)).toEqual([1, 2, 3, 4]);
    const [path, init] = fetchMock.mock.calls[0];
    const url = new URL(path, 'http://localhost');
    expect(url.pathname).toBe('/api/events');
    expect(Object.fromEntries(url.searchParams))
      .toEqual({ name: 'React & UX', page: '1', items_per_page: '4' });
    expect(init.signal).toBe(signal);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('rechaza una respuesta incompatible con el contrato', async () => {
    const get = vi.fn().mockResolvedValue({ items: 'incorrecto' });
    await expect(makeEventHttpAdapter(get).list({ name: ' ', page: 1, items_per_page: 4 }))
      .rejects.toMatchObject({ retryable: false });
    expect(get.mock.calls[0][0]).toBe('/events?page=1&items_per_page=4');
  });

  it('presenta un error recuperable sin exponer detalles internos del servidor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'Detalle interno' }, { status: 500 })));
    await expect(getJson('/events')).rejects.toMatchObject({
      retryable: true,
      message: 'El servidor no pudo completar la solicitud. Inténtalo de nuevo.',
    });
  });
});
