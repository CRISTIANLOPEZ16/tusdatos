import { makeRegistrationHttpAdapter } from '../infrastructure/http/registration-http-adapter';
import { makeEventManagementHttpAdapter } from '../infrastructure/http/event-management-http-adapter';
import { makeSessionHttpAdapter } from '../infrastructure/http/session-http-adapter';
import type { QueryClient } from '@tanstack/react-query';
import { makeEventHttpAdapter } from '../infrastructure/http/event-http-adapter';
import { makeAuthHttpAdapter } from '../infrastructure/http/auth-http-adapter';
import { makePrivateHttpClient } from '../infrastructure/http/private-http-client';
import { getJson, requestJson } from '../infrastructure/http/http-client';
import { makeSessionStore } from '../infrastructure/security/session-store';

export const dependencies = { events: makeEventHttpAdapter(getJson) };

export function createAuthDependencies(queryClient: QueryClient) {
  const sessions = makeSessionStore();
  function clearPrivateData() {
    void queryClient.cancelQueries({ queryKey: ['me'] });
    queryClient.removeQueries({ queryKey: ['me'] });
  }
  function endSession(expectedToken?: string) {
    if (expectedToken && sessions.getSnapshot()?.access_token !== expectedToken) return;
    sessions.set(null);
    clearPrivateData();
  }
  const http = makePrivateHttpClient(sessions, endSession);
  return {
    registration: makeRegistrationHttpAdapter(requestJson),
    management: { events: makeEventManagementHttpAdapter(requestJson, http), sessions: makeSessionHttpAdapter(http) },
    sessions,
    auth: makeAuthHttpAdapter(requestJson),
    http,
    clearPrivateData,
    endSession,
  };
}
