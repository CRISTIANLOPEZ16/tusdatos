import { readJwtSession } from '../../src/infrastructure/security/jwt-session';

export function fakeJwt({ sub = '7', exp = Math.floor(Date.now() / 1000) + 600 } = {}) {
  const encode = (value: unknown) => btoa(JSON.stringify(value))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  return `${encode({ alg: 'HS256', typ: 'JWT' })}.${encode({
    sub, iat: Math.floor(Date.now() / 1000), exp,
  })}.c2lnbmF0dXJl`;
}

export function sessionFor(userId = '7') {
  return readJwtSession(fakeJwt({ sub: userId }), `user${userId}@example.com`);
}
