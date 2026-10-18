import { AppError } from '../../domain/errors';
import { errorSchema } from './schemas';

export type HttpGet = (path: string, signal?: AbortSignal) => Promise<unknown>;

export const getJson: HttpGet = async (path, signal) => {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      signal,
      headers: { Accept: 'application/json' },
    });
  } catch (error) {
    if (signal?.aborted || (error instanceof DOMException && error.name === 'AbortError')) {
      throw error;
    }
    throw new AppError('No pudimos conectar con el servidor. Inténtalo de nuevo.', true);
  }

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const parsed = errorSchema.safeParse(body);
    const serverError = response.status >= 500;
    throw new AppError(serverError
      ? 'El servidor no pudo cargar los eventos. Inténtalo de nuevo.'
      : parsed.success ? parsed.data.detail : 'Revisa los parámetros de búsqueda.',
    serverError);
  }

  try {
    return await response.json();
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new AppError('La API devolvió una respuesta inesperada.');
  }
};
