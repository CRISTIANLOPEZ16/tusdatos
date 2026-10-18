import { describe, expect, it } from 'vitest';
import { readEventQuery } from '../../src/presentation/events/event-query';

describe('parámetros del listado', () => {
  it('vuelve a la primera página cuando la URL tiene una página inválida', () => {
    expect(readEventQuery(new URLSearchParams('page=0')).page).toBe(1);
  });
});
