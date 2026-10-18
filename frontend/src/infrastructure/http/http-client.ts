import { AppError } from '../../domain/errors';
import { errorSchema } from './schemas';

export type HttpGet = (path: string, signal?: AbortSignal) => Promise<unknown>;
export type HttpClient = (path: string, options?: RequestInit) => Promise<unknown>;

export class HttpError extends AppError {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message, status >= 500);
    this.name = 'HttpError';
    this.status = status;
  }
}

export const requestJson: HttpClient = async (path, options = {}) => {
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  if (options.body !== undefined) headers.set('Content-Type', 'application/json');
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...options, headers });
  } catch (error) {
    if (options.signal?.aborted || (error instanceof DOMException && error.name === 'AbortError')) {
      throw error;
    }
    throw new AppError('No pudimos conectar con el servidor. Inténtalo de nuevo.', true);
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const parsed = errorSchema.safeParse(body);
    throw new HttpError(response.status, response.status >= 500
      ? 'El servidor no pudo completar la solicitud. Inténtalo de nuevo.'
      : parsed.success ? parsed.data.detail : 'Revisa los datos enviados.');
  }
  if (response.status === 204) return undefined;
  try {
    return await response.json();
  } catch (error) {
    if (options.signal?.aborted) throw error;
    throw new AppError('La API devolvió una respuesta inesperada.');
  }
};

export const getJson: HttpGet = (path, signal) => requestJson(path, { signal });
