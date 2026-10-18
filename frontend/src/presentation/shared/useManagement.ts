import { createContext, useContext } from 'react';
import type { EventManagementPort } from '../../application/ports/event-port';
import type { SessionPort } from '../../application/ports/session-port';
export interface Management {
  events: EventManagementPort;
  sessions: SessionPort;
}
export const ManagementContext = createContext<Management | null>(null);
export function useManagement() {
  const value = useContext(ManagementContext);
  if (!value) throw new Error('Falta ManagementContext.');
  return value;
}
