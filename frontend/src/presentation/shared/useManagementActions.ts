import { useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { EventInput } from '../../domain/event';
import type { SessionInput } from '../../domain/session';
import { useManagement } from './useManagement';
import { useAuth } from '../auth/useAuth';
export function useManagementActions() {
  const api = useManagement();
  const client = useQueryClient();
  const { user } = useAuth();
  const lock = useRef(false);
  const userId = user?.user_id;
  function refresh(eventId: number) {
    void client.invalidateQueries({ queryKey: ['events'] });
    void client.invalidateQueries({ queryKey: ['event-detail', eventId] });
    void client.invalidateQueries({ queryKey: ['me', userId] });
  }
  const event = useMutation({
    mutationFn: ({ id, input }: { id?: number; input: EventInput }) => id ? api.events.update(id, input) : api.events.create(input),
    onSuccess: data => refresh(data.event_id), retry: false,
  });
  const session = useMutation({
    mutationFn: ({ id, input }: { id: number; input: SessionInput }) => api.sessions.create(id, input),
    onSuccess: data => refresh(data.event_id), retry: false,
  });
  const registration = useMutation({
    mutationFn: ({ eventId, sessionId }: { eventId: number; sessionId: number }) => api.sessions.register(eventId, sessionId),
    onSuccess: data => refresh(data.event_id),
    onError: (_error, variables) => { refresh(variables.eventId); }, retry: false,
  });
  async function run<T>(action: () => Promise<T>) {
    if (lock.current) throw new Error('Espera a que termine la solicitud actual.');
    lock.current = true;
    try { return await action(); } finally { lock.current = false; }
  }
  return { event, session, registration, run };
}
