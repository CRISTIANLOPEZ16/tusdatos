import { useState } from 'react';
import { useQueries, useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router';
import { Alert, Box, Button, Container, Divider, Link, Pagination, Snackbar, Stack, Typography } from '@mui/material';
import { useAuth } from '../auth/useAuth';
import { useManagement } from '../shared/useManagement';
import { EventIcon, QueryFeedback, Schedule, Section, Status } from '../shared/ManagementUi';
import { ManagementDialogs } from '../events/ManagementDialogs';
import type { Editor } from '../events/ManagementDialogs';

export default function MyDashboardPage() {
  const { user, logout } = useAuth();
  const api = useManagement();
  const [eventPage, setEventPage] = useState(1);
  const [sessionPage, setSessionPage] = useState(1);
  const [editor, setEditor] = useState<Editor | null>(null);
  const [notice, setNotice] = useState('');
  const events = useQuery({ queryKey: ['me', user?.user_id, 'events', eventPage],
    queryFn: ({ signal }) => api.events.mine(eventPage, signal), enabled: !!user, retry: false });
  const sessions = useQuery({ queryKey: ['me', user?.user_id, 'sessions', sessionPage],
    queryFn: ({ signal }) => api.sessions.mine(sessionPage, signal), enabled: !!user, retry: false });
  const eventIds = [...new Set(sessions.data?.items.map(s => s.event_id) ?? [])];
  const details = useQueries({ queries: eventIds.map(id => ({ queryKey: ['event-detail', id],
    queryFn: ({ signal }: { signal: AbortSignal }) => api.events.detail(id, signal), staleTime: 30_000, retry: false })) });
  const eventNames = new Map(details.flatMap(q => q.data ? [[q.data.event_id, q.data.name] as const] : []));
  return <Container component="main" maxWidth="lg" sx={{ py: { xs: 3, sm: 5 } }}>
    <Typography component="h1" sx={{ fontSize: { xs: 32, sm: 42 }, fontWeight: 800, letterSpacing: -1.5, mb: 3 }}>Mi dashboard</Typography>
    <Stack spacing={3}>
      <Section><Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} sx={{ alignItems: { sm: 'center' }, justifyContent: 'space-between' }}>
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center', minWidth: 0 }}><EventIcon /><Box sx={{ minWidth: 0 }}>
          <Typography component="h2" variant="h6" sx={{ fontWeight: 800 }}>¡Hola!</Typography>
          <Typography>Ya estás dentro.</Typography><Typography color="text.secondary" sx={{ overflowWrap: 'anywhere' }}>{user?.email}</Typography>
        </Box></Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button component={RouterLink} to="/eventos" variant="contained">Volver a eventos</Button>
          <Button variant="outlined" onClick={logout}>Cerrar sesión</Button>
        </Stack>
      </Stack></Section>
      <Section><Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ justifyContent: 'space-between', mb: 3 }}>
        <Box><Typography component="h2" variant="h5" sx={{ fontWeight: 800 }}>Mis eventos como organizador</Typography>
          <Typography color="text.secondary">Gestiona tus eventos y agrega nuevas sesiones.</Typography></Box>
        <Button variant="contained" onClick={() => setEditor({ type: 'event' })}>+ Crear evento</Button>
      </Stack>
        <QueryFeedback pending={events.isPending} fetching={events.isFetching} error={events.error} retry={() => { void events.refetch(); }} />
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, minmax(0, 1fr))' }, gap: 2 }}>
          {events.data?.items.map(event => <Section key={event.event_id}>
            <Stack spacing={2} sx={{ height: '100%', overflowWrap: 'anywhere' }}>
              <Stack direction="row" sx={{ justifyContent: 'space-between' }}><EventIcon /><Status status={event.status} /></Stack>
              <Typography component="h3" variant="h6" sx={{ fontWeight: 800 }}><Link component={RouterLink} to={`/eventos/${event.event_id}`} color="inherit" underline="hover" sx={{ '&::after': { content: '""', position: 'absolute', inset: 0, borderRadius: 3 }, '&:focus-visible::after': { outline: '3px solid #285BD4' } }}>{event.name}</Link></Typography>
              {event.description && <Typography color="text.secondary">{event.description}</Typography>}
              <Divider /><Schedule start={event.starts_at} end={event.ends_at} address={event.address} />
              <Button sx={{ position: 'relative', zIndex: 1 }} variant="outlined" onClick={() => setEditor({ type: 'session', event })}>+ Agregar nueva sesión</Button>
              <Button sx={{ position: 'relative', zIndex: 1 }} onClick={() => setEditor({ type: 'event', initial: event })}>Editar evento</Button>
            </Stack>
          </Section>)}
        </Box>
        {events.data?.items.length === 0 && <Alert severity="info">{events.data.total ? 'Esta página quedó vacía.' : 'Aún no has creado eventos.'}</Alert>}
        {(events.data?.total ?? 0) > 0 && <Pagination sx={{ mt: 3 }} color="primary" aria-label="Páginas de mis eventos" page={eventPage} count={Math.max(eventPage, Math.ceil((events.data?.total ?? 0) / 6))} onChange={(_, page) => setEventPage(page)} />}
        {events.data?.items.length === 0 && eventPage > 1 && <Button onClick={() => setEventPage(1)}>Volver a la primera página de eventos</Button>}
      </Section>
      <Section><Typography component="h2" variant="h5" sx={{ fontWeight: 800 }}>Mis inscripciones a sesiones</Typography>
        <Typography color="text.secondary">Aquí puedes ver las sesiones a las que te has inscrito.</Typography>
        <QueryFeedback pending={sessions.isPending} fetching={sessions.isFetching} error={sessions.error} retry={() => { void sessions.refetch(); }} />
        {details.some(q => q.isError) && <Alert severity="warning" sx={{ mb: 2 }} action={<Button color="inherit" onClick={() => { details.filter(q => q.isError).forEach(q => { void q.refetch(); }); }}>Reintentar</Button>}>Algunos nombres de eventos no pudieron cargarse. Tus inscripciones siguen visibles.</Alert>}
        <Stack spacing={1.5}>{sessions.data?.items.map(session => <Section key={session.session_id}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: { sm: 'center' }, overflowWrap: 'anywhere' }}>
            <EventIcon /><Box sx={{ flex: 1 }}><Typography component="h3" variant="h6" sx={{ fontWeight: 800 }}>{eventNames.get(session.event_id) ?? `Evento #${session.event_id}`}</Typography>
              <Typography>Sesión: {session.title}</Typography>
              <Typography variant="body2" color="text.secondary">Ponentes: {session.speaker_names.join(', ') || 'Por confirmar'}</Typography>
            </Box><Schedule start={session.starts_at} end={session.ends_at} />
          </Stack>
        </Section>)}</Stack>
        {sessions.data?.items.length === 0 && <Alert severity="info">{sessions.data.total ? 'Esta página quedó vacía.' : 'Aún no tienes inscripciones a sesiones.'}</Alert>}
        {(sessions.data?.total ?? 0) > 0 && <Pagination sx={{ mt: 3 }} color="primary" aria-label="Páginas de mis inscripciones" page={sessionPage} count={Math.max(sessionPage, Math.ceil((sessions.data?.total ?? 0) / 5))} onChange={(_, page) => setSessionPage(page)} />}
        {sessions.data?.items.length === 0 && sessionPage > 1 && <Button onClick={() => setSessionPage(1)}>Volver a la primera página de inscripciones</Button>}
      </Section>
    </Stack>
    {editor && <ManagementDialogs editor={editor} onClose={() => setEditor(null)} onSaved={message => { setEditor(null); setNotice(message); }} />}
    <Snackbar open={!!notice} autoHideDuration={6000} onClose={() => setNotice('')}><Alert severity="success" onClose={() => setNotice('')}>{notice}</Alert></Snackbar>
  </Container>;
}
