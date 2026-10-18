import { z } from 'zod';
import type { AuthPort } from '../../application/ports/auth-port';
import { AppError } from '../../domain/errors';
import { readJwtSession } from '../security/jwt-session';
import { HttpError } from './http-client';
import type { HttpClient } from './http-client';

const tokenResponseSchema = z.object({
  access_token: z.string().min(1),
  token_type: z.literal('bearer'),
});

export function makeAuthHttpAdapter(http: HttpClient): AuthPort {
  return {
    async login(credentials, signal) {
      const email = credentials.email.trim().toLowerCase();
      if (!email || credentials.password.length === 0) {
        throw new AppError('Completa el correo y la contraseña.');
      }
      try {
        const raw = await http('/auth/login', {
          method: 'POST', signal,
          body: JSON.stringify({ email, password: credentials.password }),
        });
        const parsed = tokenResponseSchema.safeParse(raw);
        if (!parsed.success) throw new AppError('El servidor devolvió una sesión inesperada.');
        return readJwtSession(parsed.data.access_token, email);
      } catch (error) {
        if (error instanceof HttpError && error.status === 401) {
          throw new AppError('Correo o contraseña incorrectos.');
        }
        if (error instanceof HttpError && error.status === 422) {
          throw new AppError('Revisa el formato del correo y completa la contraseña.');
        }
        throw error;
      }
    },
  };
}
