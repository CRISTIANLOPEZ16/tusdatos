import { Link as RouterLink } from 'react-router';
import { Link } from '@mui/material';
import { Box, Chip, Paper, Stack, Typography } from '@mui/material';
import type { EventStatus, EventSummary } from '../../domain/event';

const dateFormat = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric', month: 'long', year: 'numeric', timeZone: 'America/Bogota',
});
const timeFormat = new Intl.DateTimeFormat('es-CO', {
  hour: 'numeric', minute: '2-digit', timeZone: 'America/Bogota',
});
const labels: Record<EventStatus, string> = {
  activo: 'Activo', cancelado: 'Cancelado', finalizado: 'Finalizado',
  borrador: 'Borrador', archivado: 'Archivado',
};

export function EventCard({ event, to }: { event: EventSummary; to?: string }) {
  const start = new Date(event.starts_at);
  const initials = event.name.split(/\s+/).slice(0, 2).map((word) => word[0]).join('').toLocaleUpperCase('es-CO');
  return (
    <Paper component="article" variant="outlined" sx={{
      position: 'relative', p: { xs: 2, sm: 3 }, borderColor: '#E9E5EF', borderRadius: 3,
      display: 'flex', alignItems: 'center', gap: { xs: 2, sm: 3 },
    }}>
      <Box sx={{ flex: 1, minWidth: 0, overflowWrap: 'anywhere' }}>
        <Typography component="p" sx={{ color: 'primary.main', fontSize: 12, fontWeight: 650, mb: 1 }}>
          <time dateTime={event.starts_at}>{dateFormat.format(start)} · {timeFormat.format(start)}</time>
        </Typography>
        <Typography component="h3" sx={{ fontSize: { xs: 18, sm: 22 }, fontWeight: 750, lineHeight: 1.3, mb: 1 }}>
          <Link component={RouterLink} to={to ?? `/eventos/${event.event_id}`} color="inherit" underline="hover" sx={{ '&::after': { content: '""', position: 'absolute', inset: 0, borderRadius: 3 }, '&:focus-visible::after': { outline: '3px solid #285BD4' } }}>{event.name}</Link>
        </Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 13, overflowWrap: 'anywhere' }}>
          {event.address}
        </Typography>
        {event.description && (
          <Typography sx={{ color: 'text.secondary', fontSize: 13, mt: 1,
            display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
            {event.description}
          </Typography>
        )}
        <Stack direction="row" sx={{ mt: 1.5 }}>
          <Chip label={labels[event.status]} size="small" sx={{
            bgcolor: event.status === 'activo' ? '#EEF3FF' : '#F3F1F6',
            color: event.status === 'activo' ? 'secondary.main' : 'text.secondary',
            fontWeight: 650, fontSize: 11, borderRadius: 1,
          }} />
        </Stack>
      </Box>
      <Box aria-hidden="true" sx={{
        flexShrink: 0, width: { xs: 66, sm: 126 }, height: { xs: 86, sm: 126 },
        borderRadius: 2.5, bgcolor: event.event_id % 2 ? '#F0E7FF' : '#E7EFFF',
        color: event.event_id % 2 ? 'primary.main' : 'secondary.main',
        display: 'grid', placeItems: 'center', fontSize: { xs: 25, sm: 42 }, fontWeight: 800,
      }}>{initials}</Box>
    </Paper>
  );
}
