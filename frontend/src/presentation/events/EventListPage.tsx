import { useState } from 'react';
import type { FormEvent } from 'react';
import { Alert, Box, Button, Chip, Container, InputAdornment, LinearProgress, Paper,
  Skeleton, Stack, SvgIcon, TextField, Typography } from '@mui/material';
import { EventCard } from './EventCard';
import { useNavigate, useParams } from 'react-router';
import { readEventQuery } from './event-query';
import { Pagination } from '../shared/Pagination';
import { useEvents } from './useEvents';
import { AuthNavigationButton } from '../auth/AuthNavigationButton';

function EventSearch({ initialName, onSearch }:
  { initialName: string; onSearch: (name: string) => void }) {
  const [value, setValue] = useState(initialName);
  const invalid = value.trim().length > 150;
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!invalid) onSearch(value.trim());
  }
  return (
    <Box component="form" role="search" onSubmit={submit} sx={{ display: 'flex', gap: 1.5, width: '100%', mb: 5 }}>
      <TextField fullWidth size="small" value={value} error={invalid}
        onChange={(event) => setValue(event.target.value)} placeholder="Buscar eventos por nombre"
        helperText={invalid ? 'Usa un máximo de 150 caracteres.' : undefined}
        slotProps={{ htmlInput: { 'aria-label': 'Buscar eventos por nombre', maxLength: 150 },
          input: { startAdornment: <InputAdornment position="start"><SvgIcon aria-hidden="true" sx={{ fontSize: 20 }}>
            <path d="m21 21-4.5-4.5M10.5 18a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15Z"
              fill="none" stroke="currentColor" strokeWidth="1.7" />
          </SvgIcon></InputAdornment> } }}
        sx={{ '& .MuiOutlinedInput-root': { minHeight: 49, bgcolor: '#FCFBFE', borderRadius: 2 },
          '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E4DDEE' }, '& input': { fontSize: 13 } }} />
      <Button type="submit" variant="contained" disabled={invalid} sx={{ height: 49 }}>Buscar</Button>
    </Box>
  );
}

export default function EventListPage() {
  const { page, name } = useParams();
  const navigateTo = useNavigate();

  const params = readEventQuery(
    new URLSearchParams({
      name: name ?? '',
      page: page ?? '1',
    }),
  );
  const invalidName = (params.name?.length ?? 0) > 150;
  const query = useEvents(params);
  const data = query.data;

  function navigate(name: string, page: number) {
    const base = name
    ? `/eventos/buscar/${encodeURIComponent(name)}`
    : '/eventos';
    navigateTo(
      page > 1 ? `${base}/page/${page}` : base
    );
  }

  return (
    <>
      <Box component="header" sx={{ borderBottom: '1px solid #EEEAF3' }}>
        <Container maxWidth={false} sx={{ maxWidth: 1104, py: 2.5, px: { xs: 2.5, sm: 4 } }}>
          <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <Box sx={{ width: 35, height: 35, bgcolor: 'primary.main', color: 'white', borderRadius: 2, display: 'grid', placeItems: 'center' }}>
                <SvgIcon aria-hidden="true" sx={{ fontSize: 25 }}>
                  <path d="m12 2 2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6L12 2Z"
                    fill="none" stroke="currentColor" strokeWidth="1.7" />
                </SvgIcon>
              </Box>
              <Typography sx={{ fontSize: { xs: 19, sm: 22 }, fontWeight: 800, letterSpacing: -1 }}>
                mis<Box component="span" sx={{ color: 'primary.main' }}>eventos</Box>
              </Typography>
            </Stack>
            <Stack direction="row" spacing={{ xs: 0, sm: 4 }} sx={{ alignItems: 'center' }}>
              <Typography sx={{ display: { xs: 'none', sm: 'block' }, color: 'primary.main', fontSize: 13, fontWeight: 700 }}>
                Explorar eventos
              </Typography>
              <AuthNavigationButton />
            </Stack>
          </Stack>
        </Container>
      </Box>
      <Container component="main" maxWidth={false} sx={{ maxWidth: 1040, px: { xs: 2.5, sm: 4 }, pt: { xs: 5, sm: 7 }, pb: 5 }}>
        <Typography sx={{ color: 'secondary.main', fontSize: 10, letterSpacing: 1.7, fontWeight: 750, mb: 1.5 }}>
          DESCUBRE. CONECTA. COMPARTE.
        </Typography>
        <Typography component="h1" sx={{ fontSize: { xs: 35, sm: 49 }, fontWeight: 780, lineHeight: 1.12, letterSpacing: -1.8 }}>
          Tu próximo encuentro<br /><Box component="span" sx={{ color: 'primary.main' }}>empieza aquí.</Box>
        </Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 15, mt: 2, mb: 3.5 }}>
          Encuentra eventos, descubre nuevas ideas y conecta con tu comunidad.
        </Typography>
        <EventSearch key={params.name ?? ''} initialName={params.name ?? ''}
          onSearch={(name) => navigate(name, 1)} />

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ justifyContent: 'space-between',
          alignItems: { xs: 'flex-start', sm: 'center' }, borderBottom: '1px solid #EEEAF3', pb: 2 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Typography component="h2" sx={{ fontSize: 19, fontWeight: 750 }}>
              {params.name ? 'Resultados de búsqueda' : 'Eventos'}
            </Typography>
            {data && <Chip label={data.total} size="small" sx={{ bgcolor: '#F2ECFC', color: 'primary.main', fontWeight: 700 }} />}
          </Stack>
          <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>Hora de Bogotá · GMT−5</Typography>
        </Stack>
        <Box sx={{ height: 4, mb: 3 }}>
          {query.isFetching && !query.isPending && <LinearProgress aria-label="Actualizando eventos" />}
        </Box>

        <Box aria-live="polite" aria-atomic="true" sx={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clipPath: 'inset(50%)' }}>
          {query.isFetching ? 'Cargando eventos…' : data ? `${data.total} eventos. Página ${params.page}.` : ''}
        </Box>

        {invalidName ? <Alert severity="warning">La búsqueda no puede superar 150 caracteres.</Alert> : (
          <>
            {query.isError && <Alert severity="error" sx={{ mb: 2 }} action={
              <Button type="button" color="inherit" onClick={() => void query.refetch()}>Reintentar</Button>
            }>{query.error instanceof Error ? query.error.message : 'No pudimos cargar los eventos.'}</Alert>}

            {query.isPending && <Stack role="status" aria-label="Cargando eventos" spacing={2}>
              {[0, 1, 2, 3].map((id) => <Skeleton key={id} variant="rounded" height={185} />)}
            </Stack>}

            {data && <Box aria-busy={query.isFetching}>
              <Stack spacing={2}>{data.items.map((event) => <EventCard key={event.event_id} event={event} to={`/eventos/${event.event_id}`} />)}</Stack>
              {data.items.length === 0 && <Paper variant="outlined" sx={{ p: 4, textAlign: 'center', borderColor: '#E9E5EF' }}>
                <Typography component="h3" sx={{ fontWeight: 700, mb: 1 }}>
                  {data.total > 0 ? 'Esta página ya no tiene eventos' : params.name ? 'No encontramos eventos' : 'Todavía no hay eventos publicados'}
                </Typography>
                <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>
                  {data.total > 0 ? 'Vuelve a la primera página para consultar los resultados actuales.' : params.name ? `No hay resultados para «${params.name}». Prueba otro nombre.` : 'Vuelve pronto para descubrir nuevos encuentros.'}
                </Typography>
                {(params.name || data.total > 0) && <Button type="button" sx={{ mt: 2 }}
                  onClick={() => navigate(data.total > 0 ? params.name ?? '' : '', 1)}>
                  {data.total > 0 ? 'Ir a la primera página' : 'Limpiar búsqueda'}
                </Button>}
              </Paper>}
              <Pagination page={params.page} total={data.total} itemsPerPage={data.items_per_page}
                onChange={(page) => navigate(params.name ?? '', page)} />
            </Box>}
          </>
        )}
        <Box component="footer" sx={{ borderTop: '1px solid #EEEAF3', mt: 5, pt: 3 }}>
          <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>Hecho para encontrarnos.</Typography>
        </Box>
      </Container>
    </>
  );
}
