import type { Credentials } from '../../domain/auth';
import type { RegisteredUser } from '../../domain/registration';
export interface RegistrationPort {
  register(credentials: Credentials, signal?: AbortSignal): Promise<RegisteredUser>;
}
