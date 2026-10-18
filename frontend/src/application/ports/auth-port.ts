import type { AuthSession, Credentials } from '../../domain/auth';

export interface AuthPort {
  login(credentials: Credentials, signal?: AbortSignal): Promise<AuthSession>;
}

export interface SessionStorePort {
  getSnapshot(): AuthSession | null;
  subscribe(listener: () => void): () => void;
  set(session: AuthSession | null): void;
}