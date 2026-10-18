import { afterEach, describe, expect, it, vi } from 'vitest';
import { AppError } from '../../src/domain/errors';
import { getJson } from '../../src/infrastructure/http/http-client';
import { makeEventHttpAdapter } from '../../src/infrastructure/http/event-http-adapter';
import { firstPage } from '../fixtures/events';

afterEach(() => vi.unstubAllGlobals());

describe('listado HTTP', () => {
  it('envía filtro/paginación y señal, conservando el orden de la API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(Response.json(firstPage));
    vi.stubGlobal('fetch', fetchMock);
    const signal = new AbortController().signal;
    const result = await makeEventHttpAdapter(getJson).list({
      name: 'React & UX', page: 1, items_per_page: 4,
    }, signal);
    expect(result.items.map((event) => event.event_id)).toEqual([1, 2, 3, 4]);
    expect(Date.parse(result.items[0].starts_at)).toBeGreaterThan(Date.parse(result.items[1].starts_at));
    const [path, init] = fetchMock.mock.calls[0];
    const url = new URL(path, 'http://localhost');
    expect(url.pathname).toBe('/api/events');
    expect(Object.fromEntries(url.searchParams))
      .toEqual({ name: 'React & UX', page: '1', items_per_page: '4' });
    expect(init.signal).toBe(signal);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('omite name vacío y rechaza un contrato inesperado', async () => {
    const get = vi.fn().mockResolvedValue({ items: 'incorrecto' });
    await expect(makeEventHttpAdapter(get).list({ name: ' ', page: 1, items_per_page: 4 }))
      .rejects.toMatchObject({ retryable: false });
    expect(get.mock.calls[0][0]).toBe('/events?page=1&items_per_page=4');
  });

  it.each([422, 500])('controla errores HTTP %s sin exponer detalles de 5xx', async (status) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'Detalle interno' }, { status })));
    await expect(getJson('/events')).rejects.toMatchObject({ retryable: status === 500 });
    if (status === 500) {
      await expect(getJson('/events')).rejects.not.toThrow('Detalle interno');
    }
  });

  it('interpreta la lista de errores 422 como entrada inválida', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: [{ loc: ['query', 'name'], msg: 'Invalid' }] }, { status: 422 })));
    await expect(getJson('/events')).rejects.toThrow('Revisa los datos enviados.');
  });

  it('rechaza JSON inválido sin reintento automático', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>Error</html>')));
    await expect(getJson('/events')).rejects.toMatchObject({ retryable: false });
  });

  it('distingue una desconexión de una cancelación', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(getJson('/events')).rejects.toEqual(expect.any(AppError));
    await expect(getJson('/events')).rejects.toMatchObject({ retryable: true });
    const abort = new DOMException('Aborted', 'AbortError');
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(abort));
    await expect(getJson('/events')).rejects.toBe(abort);
  });
});
