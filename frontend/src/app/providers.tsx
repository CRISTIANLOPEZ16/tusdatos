import { useState } from 'react';
import type { PropsWithChildren } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { EventPort } from '../application/ports/event-port';
import { EventPortContext } from '../presentation/events/useEvents';
import { theme } from '../presentation/styles/theme';
import { dependencies } from './dependencies';

export function Providers({ children, events = dependencies.events }:
  PropsWithChildren<{ events?: EventPort }>) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <EventPortContext.Provider value={events}>{children}</EventPortContext.Provider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
