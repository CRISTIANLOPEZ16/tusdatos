import { Alert, Avatar, Box, Button, Chip, LinearProgress, Paper, Stack, SvgIcon, Typography } from '@mui/material';
import type { PropsWithChildren } from 'react';
import type { EventStatus } from '../../domain/event';
import { scheduleLabel } from './schedule';
export function Section({ children }: PropsWithChildren) {
  return <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, borderColor: '#E7E1F2', borderRadius: 3, position: 'relative' }}>{children}</Paper>;
}
export function EventIcon() {
  return <Avatar variant="rounded" sx={{ bgcolor: '#EEE7FF', color: 'primary.main', width: 64, height: 64 }}>
    <SvgIcon aria-hidden="true"><path d="M7 2v4m10-4v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" strokeWidth="1.7" /></SvgIcon>
  </Avatar>;
}
export function Status({ status }: { status: EventStatus }) {
  const labels: Record<EventStatus, string> = { activo: 'Activo', borrador: 'Borrador', cancelado: 'Cancelado', finalizado: 'Finalizado', archivado: 'Archivado' };
  return <Chip size="small" label={labels[status]} sx={{ alignSelf: 'flex-start', bgcolor: status === 'activo' ? '#E4F8EE' : '#F0ECF7', color: status === 'activo' ? '#086A52' : 'text.secondary' }} />;
}
export function Schedule({ start, end, address }: { start: string; end: string; address?: string }) {
  return <Stack spacing={1} sx={{ my: 2, color: 'text.secondary' }}>
    <Typography variant="body2">{scheduleLabel(start, end)} · Bogotá</Typography>
    {address && <Typography variant="body2">{address}</Typography>}
  </Stack>;
}
export function QueryFeedback({ pending, fetching, error, retry }: {
  pending: boolean; fetching: boolean; error: Error | null; retry: () => void;
}) {
  return <Box sx={{ my: 2 }}>
    {(pending || fetching) && <LinearProgress aria-label="Cargando información" />}
    {error && <Alert severity="error" action={<Button color="inherit" onClick={retry}>Reintentar</Button>}>{error.message}</Alert>}
  </Box>;
}
