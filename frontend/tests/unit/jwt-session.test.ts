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

  it('rechaza un token ilegible', () => {
    expect(() => readJwtSession('a.b.c', 'persona@example.com')).toThrow();
  });

  it('rechaza el token al llegar a su caducidad', () => {
    const exp = Math.floor(Date.now() / 1000) + 600;
    const token = fakeJwt({ exp });
    expect(() => readJwtSession(token, 'persona@example.com', exp * 1000)).toThrow();
  });
});
