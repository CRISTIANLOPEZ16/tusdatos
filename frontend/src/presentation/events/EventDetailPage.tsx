import { useNow } from '../shared/useNow';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink, useParams } from 'react-router';
import { Alert, Box, Button, Container, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Snackbar, Stack, Typography } from '@mui/material';
import type { Session } from '../../domain/session';
import { useAuth } from '../auth/useAuth';
import { useManagement } from '../shared/useManagement';
import { useManagementActions } from '../shared/useManagementActions';
import { EventIcon, QueryFeedback, Section, Status } from '../shared/ManagementUi';
import { dateLabel, scheduleLabel, timeLabel } from '../shared/schedule';
import { SessionCard } from '../sessions/SessionCard';
import { ManagementDialogs } from './ManagementDialogs';
import type { Editor } from './ManagementDialogs';

export default function EventDetailPage() {
  const { eventId = '' } = useParams();
  const id = Number(eventId);
  const valid = /^[1-9]\d*$/.test(eventId) && Number.isSafeInteger(id);
  const { user, isAuthenticated } = useAuth();
  const api = useManagement();
  const now = useNow();
  const actions = useManagementActions();
  const [editor, setEditor] = useState<Editor | null>(null);
  const [notice, setNotice] = useState('');
  const [confirmation, setConfirmation] = useState<Session | null>(null);
  const [confirmed, setConfirmed] = useState<Record<number, number>>({});
  const query = useQuery({ queryKey: ['event-detail', id], queryFn: ({ signal }) => api.events.detail(id, signal), enabled: valid, staleTime: 0, retry: false });
  const event = query.data;
  async function register(session: Session) {
    if (!user || actions.registration.isPending) return;
    const userId = user.user_id;
    try {
      await actions.run(() => actions.registration.mutateAsync({ eventId: id, sessionId: session.session_id }));
      setConfirmed(previous => ({ ...previous, [session.session_id]: userId }));
      setConfirmation(session);
    } catch { /* El estado de la mutación muestra el error; el cliente privado gestiona 401. */ }
  }
  return <Container component="main" maxWidth="lg" sx={{ py: { xs: 3, sm: 5 } }}>
    <Typography component="h1" sx={{ fontSize: { xs: 32, sm: 42 }, fontWeight: 800, letterSpacing: -1.5, mb: 3 }}>Detalles del evento</Typography>
    {!valid && <Alert severity="error">El identificador del evento no es válido.</Alert>}
    {valid && <QueryFeedback pending={query.isPending} fetching={query.isFetching} error={query.error} retry={() => { void query.refetch(); }} />}
    {!event && <Button component={RouterLink} to="/eventos">Volver a eventos</Button>}
    {event && <Stack spacing={4}>
      <Section><Stack direction={{ xs: 'column', md: 'row' }} spacing={3} sx={{ justifyContent: 'space-between' }}>
        <Stack direction="row" spacing={2}><EventIcon /><Box sx={{ minWidth: 0, overflowWrap: 'anywhere' }}>
          <Typography component="h2" variant="h4" sx={{ fontWeight: 800 }}>{event.name}</Typography>
          {event.description && <Typography sx={{ my: 1 }} color="text.secondary">{event.description}</Typography>}
          <Status status={event.status} />
        </Box></Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ flexShrink: 0, alignItems: 'flex-start' }}>
          <Button component={RouterLink} to="/eventos" variant="contained">Volver a eventos</Button>
          {isAuthenticated && <Button component={RouterLink} to="/my-dashboard" variant="outlined">Volver a mi dashboard</Button>}
        </Stack>
      </Stack><Divider sx={{ my: 3 }} /><Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 3 }}>
          <Box><Typography color="text.secondary">Fecha</Typography><Typography>{dateLabel(event.starts_at)}{dateLabel(event.starts_at) !== dateLabel(event.ends_at) ? ` – ${dateLabel(event.ends_at)}` : ''}</Typography></Box>
          <Box><Typography color="text.secondary">Hora de inicio</Typography><Typography>{timeLabel(event.starts_at)}</Typography></Box>
          <Box><Typography color="text.secondary">Hora de finalización</Typography><Typography>{timeLabel(event.ends_at)}</Typography></Box>
          <Box><Typography color="text.secondary">Ubicación</Typography><Typography sx={{ overflowWrap: 'anywhere' }}>{event.address}</Typography></Box>
        </Box><Typography variant="caption" color="text.secondary">Horarios de Bogotá (UTC−5).</Typography>
        {user?.user_id === event.created_by && <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button variant="outlined" onClick={() => setEditor({ type: 'session', event })}>+ Agregar nueva sesión</Button>
          <Button onClick={() => setEditor({ type: 'event', initial: event })}>Editar evento</Button>
        </Stack>}
      </Section>
      <Section><Typography component="h2" variant="h4" sx={{ fontWeight: 800 }}>Sesiones disponibles</Typography>
        <Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>Consulta la información de cada sesión y regístrate fácilmente.</Typography>
        {actions.registration.error && <Alert severity="error" sx={{ mb: 2 }}>{actions.registration.error.message}</Alert>}
        {event.sessions.length === 0 && <Alert severity="info">Este evento aún no tiene sesiones.</Alert>}
        <Stack spacing={3}>{event.sessions.map(session => <SessionCard key={session.session_id} session={session} status={event.status}
          now={now} authenticated={isAuthenticated} busy={actions.registration.isPending} confirmed={!!user && confirmed[session.session_id] === user.user_id}
          onRegister={() => { void register(session); }} />)}</Stack>
      </Section>
    </Stack>}
    {editor && <ManagementDialogs editor={editor} onClose={() => setEditor(null)} onSaved={message => { setEditor(null); setNotice(message); }} />}
    <Snackbar open={!!notice} autoHideDuration={6000} onClose={() => setNotice('')}><Alert severity="success" onClose={() => setNotice('')}>{notice}</Alert></Snackbar>
    <Dialog open={!!confirmation && isAuthenticated} onClose={() => setConfirmation(null)} aria-labelledby="registration-success-title">
      <DialogTitle id="registration-success-title">¡Felicidades!</DialogTitle>
      <DialogContent>{confirmation && <Stack spacing={2}><Typography>Te inscribiste a la sesión «{confirmation.title}».</Typography>
        <Typography>{scheduleLabel(confirmation.starts_at, confirmation.ends_at)} · Bogotá (UTC−5).</Typography></Stack>}</DialogContent>
      <DialogActions><Button onClick={() => setConfirmation(null)} autoFocus>Entendido</Button>
        <Button component={RouterLink} to="/my-dashboard" variant="contained">Ver mis inscripciones</Button></DialogActions>
    </Dialog>
  </Container>;
}
