import { createContext, useContext } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { EventPort, ListEventParams } from '../../application/ports/event-port';
import { AppError } from '../../domain/errors';

export const EventPortContext = createContext<EventPort | null>(null);

export function useEvents(params: ListEventParams) {
  const events = useContext(EventPortContext);
  if (!events) throw new Error('Falta el proveedor de eventos.');

  return useQuery({
    queryKey: ['events', params],
    queryFn: ({ signal }) => events.list(params, signal),
    enabled: (params.name?.length ?? 0) <= 150,
    staleTime: 30_000,
    retry: (attempt, error) => attempt < 1 && error instanceof AppError && error.retryable,
  });
}
