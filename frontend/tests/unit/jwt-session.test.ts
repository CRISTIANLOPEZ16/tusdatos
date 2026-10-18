import { describe, expect, it } from 'vitest';
import { readJwtSession } from '../../src/infrastructure/security/jwt-session';
import { fakeJwt } from '../fixtures/auth';

describe('lectura del JWT para presentación', () => {
  it('extrae identificador y caducidad, conservando el correo del login', () => {
    const exp = Math.floor(Date.now() / 1000) + 600;
    const result = readJwtSession(fakeJwt({ sub: '12', exp }), 'persona@example.com');
    expect(result.user_id).toBe(12);
    expect(result.expires_at).toBe(exp * 1000);
    expect(result.email).toBe('persona@example.com');
  });

  it.each(['0', '-1', 'abc', '9007199254740992'])('rechaza sub inválido: %s', (sub) => {
    expect(() => readJwtSession(fakeJwt({ sub }), 'persona@example.com')).toThrow();
  });

  it.each(['incorrecto', 'a.b.c', 'a..c'])('rechaza formato o payload inválido: %s', (token) => {
    expect(() => readJwtSession(token, 'persona@example.com')).toThrow();
  });

  it('rechaza el instante exacto de caducidad y tokens vencidos', () => {
    const exp = Math.floor(Date.now() / 1000) + 600;
    const token = fakeJwt({ exp });
    expect(() => readJwtSession(token, 'persona@example.com', exp * 1000)).toThrow();
    expect(() => readJwtSession(token, 'persona@example.com', exp * 1000 + 1)).toThrow();
  });
});
