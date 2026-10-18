import type { SessionStorePort } from '../../application/ports/auth-port';
import { AppError } from '../../domain/errors';
import { HttpError, requestJson } from './http-client';
import type { HttpClient } from './http-client';

export function makePrivateHttpClient(
  sessions: SessionStorePort,
  endSession: (expectedToken?: string) => void,
  request: HttpClient = requestJson,
): HttpClient {
  return async (path, options = {}) => {
    const session = sessions.getSnapshot();
    if (!session) throw new AppError('Inicia sesión para continuar.');
    if (session.expires_at <= Date.now()) {
      endSession(session.access_token);
      throw new AppError('Tu sesión expiró. Inicia sesión de nuevo.');
    }
    const headers = new Headers(options.headers);
    headers.set('Authorization', `Bearer ${session.access_token}`);
    try {
      const result = await request(path, { ...options, headers });
      if (sessions.getSnapshot()?.access_token !== session.access_token) {
        throw new DOMException('La sesión cambió durante la solicitud.', 'AbortError');
      }
      return result;
    } catch (error) {
      if (error instanceof HttpError && error.status === 401) {
        endSession(session.access_token);
        throw new AppError('Tu sesión dejó de estar activa. Inicia sesión de nuevo.');
      }
      throw error;
    }
  };
}
