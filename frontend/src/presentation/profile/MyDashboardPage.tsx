import { Button, Container, Paper, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router';
import { useAuth } from '../auth/useAuth';

export default function MyDashboardPage() {
  const { user, logout } = useAuth();
  return (
    <Container component="main" maxWidth="md" sx={{ py: { xs: 5, sm: 8 } }}>
      <Typography component="h1" sx={{ fontSize: 34, fontWeight: 780, letterSpacing: -1, mb: 2 }}>
        Mi dashboard
      </Typography>
      <Paper variant="outlined" sx={{ p: { xs: 3, sm: 4 }, borderColor: '#E9E5EF', borderRadius: 3 }}>
        <Typography sx={{ fontSize: 19, fontWeight: 700, mb: 1 }}>Ya estás dentro.</Typography>
        <Typography sx={{ color: 'text.secondary', mb: 3, overflowWrap: 'anywhere' }}>{user?.email}</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button component={RouterLink} to="/eventos" variant="contained">Volver a eventos</Button>
          <Button type="button" onClick={logout} variant="outlined">Cerrar sesión</Button>
        </Stack>
      </Paper>
    </Container>
  );
}
