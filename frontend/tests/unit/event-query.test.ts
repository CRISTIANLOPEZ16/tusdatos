import { describe, expect, it } from 'vitest';
import { readEventQuery } from '../../src/presentation/events/event-query';

describe('parámetros del listado', () => {
  it('omite nombre vacío y usa tamaño fijo', () => {
    expect(readEventQuery(new URLSearchParams('name=++')))
      .toEqual({ name: undefined, page: 1, items_per_page: 4 });
  });

  it('conserva búsqueda y página válidas', () => {
    expect(readEventQuery(new URLSearchParams('name=+React+&page=2')))
      .toEqual({ name: 'React', page: 2, items_per_page: 4 });
  });

  it.each(['0', '-1', '1.5', 'NaN', 'Infinity', '1e2', '9007199254740992'])(
    'normaliza una página inválida: %s', (page) => {
      expect(readEventQuery(new URLSearchParams({ page })).page).toBe(1);
    },
  );
});
