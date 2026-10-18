import { z } from 'zod';
import type { RegistrationPort } from '../../application/ports/registration-port';
import { AppError } from '../../domain/errors';
import { HttpError } from './http-client';
import type { HttpClient } from './http-client';
const userSchema = z.object({
  user_id: z.number().int().positive(), email: z.string().email(),
  created_at: z.string().datetime({ offset: true }),
});
export function makeRegistrationHttpAdapter(http: HttpClient): RegistrationPort {
  return {
    async register(credentials, signal) {
      try {
        const response = await http('/users/register', { method: 'POST', signal,
          body: JSON.stringify({ email: credentials.email.trim(), password: credentials.password }) });
        const parsed = userSchema.safeParse(response);
        if (!parsed.success) throw new AppError('No pudimos confirmar la creación de la cuenta. Intenta iniciar sesión antes de repetir el registro.');
        return parsed.data;
      } catch (error) {
        if (error instanceof HttpError && error.status === 409) throw new AppError('Este correo ya está registrado. Inicia sesión con tu cuenta.');
        if (error instanceof HttpError && error.status === 422) throw new AppError('Revisa el correo y usa una contraseña de al menos 8 caracteres.');
        throw error;
      }
    },
  };
}
