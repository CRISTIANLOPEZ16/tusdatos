import { ManagementContext } from '../presentation/shared/useManagement';
import type { Management } from '../presentation/shared/useManagement';
import { useState } from 'react';
import type { PropsWithChildren } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { EventPort } from '../application/ports/event-port';
import { EventPortContext } from '../presentation/events/useEvents';
import { AuthProvider } from '../presentation/auth/AuthProvider';
import { theme } from '../presentation/styles/theme';
import { createAuthDependencies, dependencies } from './dependencies';

export function Providers({ children, events = dependencies.events, management }:
  PropsWithChildren<{ events?: EventPort; management?: Management }>) {
  const [queryClient] = useState(() => new QueryClient());
  const [runtime] = useState(() => createAuthDependencies(queryClient));
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <AuthProvider auth={runtime.auth} sessions={runtime.sessions}
          beforeLogin={runtime.clearPrivateData} endSession={runtime.endSession}>
          <ManagementContext.Provider value={management ?? runtime.management}>
            <EventPortContext.Provider value={events}>{children}</EventPortContext.Provider>
          </ManagementContext.Provider>
        </AuthProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
