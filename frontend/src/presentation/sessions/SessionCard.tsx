import { Box, Button, Chip, Divider, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router';
import type { Session } from '../../domain/session';
import type { EventStatus } from '../../domain/event';
import { EventIcon, Schedule, Section } from '../shared/ManagementUi';
export function SessionCard({ session, status, authenticated, busy, confirmed, now, onRegister }: {
  session: Session; status: EventStatus; authenticated: boolean; busy: boolean;
  confirmed: boolean; now: number; onRegister: () => void;
}) {
  const closed = status !== 'activo' || Date.parse(session.starts_at) <= now;
  return <Section><Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}><EventIcon />
    <Typography component="h3" variant="h5" sx={{ flex: 1, fontWeight: 800, overflowWrap: 'anywhere' }}>{session.title}</Typography><Chip label="Sesión" color="primary" variant="outlined" />
  </Stack><Divider sx={{ my: 3 }} />
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2 }}>
      <Box><Typography color="text.secondary">Fecha y horario</Typography><Schedule start={session.starts_at} end={session.ends_at} /></Box>
      <Box><Typography color="text.secondary">Ponente(s)</Typography><Typography sx={{ overflowWrap: 'anywhere' }}>{session.speaker_names.join(', ') || 'Por confirmar'}</Typography></Box>
      <Box><Typography color="text.secondary">Cupos totales</Typography><Typography>{session.capacity}</Typography></Box>
      <Box><Typography color="text.secondary">Inscritos</Typography><Typography>{session.registered_count}</Typography></Box>
      <Box><Typography color="text.secondary">Cupos disponibles</Typography><Typography color="secondary.main" sx={{ fontWeight: 800 }}>{session.available_capacity}</Typography></Box>
    </Box>
    <Stack sx={{ alignItems: { xs: 'stretch', sm: 'flex-end' }, mt: 3 }}>
      {confirmed ? <Chip label="Ya estás inscrito" color="success" /> : closed ? <Typography color="text.secondary">Inscripciones cerradas</Typography> : session.available_capacity === 0 ? <Chip label="Sin cupos" /> : authenticated ?
        <Button variant="contained" disabled={busy} onClick={onRegister}>Registrarse a la sesión</Button> :
        <Button component={RouterLink} to="/login" variant="contained">Inicia sesión para inscribirte</Button>}
    </Stack>
  </Section>;
}
