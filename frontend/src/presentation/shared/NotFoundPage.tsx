import { Button, Container, Typography } from '@mui/material';
import { Link } from 'react-router';

export function NotFoundPage() {
  return (
    <Container component="main" maxWidth="sm" sx={{ py: 8 }}>
      <Typography component="h1" variant="h4" sx={{ mb: 3 }}>Página no encontrada</Typography>
      <Button component={Link} to="/eventos" variant="contained">Explorar eventos</Button>
    </Container>
  );
}
