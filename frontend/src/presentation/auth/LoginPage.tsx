import { Link as RouterLink, Navigate } from 'react-router';
import { Box, Link, Paper, Stack, SvgIcon, Typography } from '@mui/material';
import { LoginForm } from './LoginForm';
import { useAuth } from './useAuth';
import { useLogin } from './useLogin';

export default function LoginPage() {
  const { isAuthenticated } = useAuth();
  const { submit, isSubmitting, error } = useLogin();
  if (isAuthenticated) return <Navigate to="/my-dashboard" replace />;

  return (
    <Box component="main" sx={{ minHeight: '100dvh', display: 'grid', placeItems: 'center',
      bgcolor: 'background.default', px: 2.5, py: 5 }}>
      <Box sx={{ width: '100%', maxWidth: 440 }}>
        <Link component={RouterLink} to="/eventos" underline="hover" sx={{ fontSize: 13 }}>
          ← Volver a eventos
        </Link>
        <Stack direction="row" spacing={1} sx={{ justifyContent: 'center', alignItems: 'center', mt: 4, mb: 3 }}>
          <Box sx={{ width: 38, height: 38, display: 'grid', placeItems: 'center',
            bgcolor: 'primary.main', color: 'white', borderRadius: 2 }}>
            <SvgIcon aria-hidden="true"><path
              d="m12 2 2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6L12 2Z"
              fill="none" stroke="currentColor" strokeWidth="1.7" /></SvgIcon>
          </Box>
          <Typography sx={{ fontSize: 25, fontWeight: 800, letterSpacing: -1 }}>
            mis<Box component="span" sx={{ color: 'primary.main' }}>eventos</Box>
          </Typography>
        </Stack>
        <Typography component="h1" sx={{ fontSize: { xs: 29, sm: 33 }, fontWeight: 780,
          textAlign: 'center', letterSpacing: -1, lineHeight: 1.2 }}>
          Qué bueno verte de nuevo
        </Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 14, textAlign: 'center', mt: 1.5, mb: 3 }}>
          Inicia sesión y sigue conectando con tu comunidad.
        </Typography>
        <Paper variant="outlined" sx={{ p: { xs: 2.5, sm: 4 }, borderRadius: 3,
          borderColor: '#E9E5EF', boxShadow: '0 8px 32px #211B3505' }}>
          <LoginForm onSubmit={submit} isSubmitting={isSubmitting} error={error} />
        </Paper>
        <Typography sx={{ color: 'secondary.main', fontSize: 12, textAlign: 'center', mt: 3 }}>
          Tu próximo encuentro empieza aquí.
        </Typography>
      </Box>
    </Box>
  );
}
