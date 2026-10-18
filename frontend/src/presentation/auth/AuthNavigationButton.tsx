import { Button } from '@mui/material';
import { Link as RouterLink } from 'react-router';
import { useAuth } from './useAuth';

export function AuthNavigationButton() {
  const { isAuthenticated } = useAuth();
  return (
    <Button component={RouterLink} to={isAuthenticated ? '/my-dashboard' : '/login'}
      variant="outlined" sx={{ px: { xs: 1.5, sm: 2.5 }, fontSize: { xs: 12, sm: 14 } }}>
      {isAuthenticated ? 'Dashboard' : 'Iniciar sesión'}
    </Button>
  );
}
