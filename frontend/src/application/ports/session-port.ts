import type { Registration, Session, SessionInput, SessionPage } from '../../domain/session';
export interface SessionPort {
  mine(page: number, signal?: AbortSignal): Promise<SessionPage>;
  create(eventId: number, input: SessionInput): Promise<Session>;
  register(eventId: number, sessionId: number): Promise<Registration>;
}
