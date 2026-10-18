import { z } from 'zod';
import type { SessionStorePort } from '../../application/ports/auth-port';
import type { AuthSession } from '../../domain/auth';
import { AppError } from '../../domain/errors';
import { readJwtSession } from './jwt-session';

export const SESSION_KEY = 'mis-eventos.session.v1';

const storedSessionSchema = z.object({
  access_token: z.string().min(1),
  token_type: z.literal('bearer'),
  email: z.string().min(1),
});

function removeStoredSession() {
  try {
    window.sessionStorage.removeItem(SESSION_KEY);
  } catch {
    // El estado en memoria se limpia aunque el navegador bloquee storage.
  }
}

function restoreSession(): AuthSession | null {
  try {
    const raw = window.sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const stored = storedSessionSchema.parse(JSON.parse(raw));
    return readJwtSession(stored.access_token, stored.email);
  } catch {
    removeStoredSession();
    return null;
  }
}

export function makeSessionStore(): SessionStorePort {
  let current = restoreSession();
  const listeners = new Set<() => void>();
  return {
    getSnapshot: () => current,
    subscribe(listener) {
      listeners.add(listener);
      return () => { listeners.delete(listener); };
    },
    set(next) {
      if (next) {
        try {
          window.sessionStorage.setItem(SESSION_KEY, JSON.stringify({
            access_token: next.access_token, token_type: next.token_type, email: next.email,
          }));
        } catch {
          throw new AppError('No se pudo guardar la sesión. Habilita el almacenamiento de esta pestaña e inténtalo de nuevo.');
        }
      } else {
        removeStoredSession();
      }
      current = next;
      listeners.forEach((listener) => listener());
    },
  };
}
