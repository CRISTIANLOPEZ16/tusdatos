import { useState } from 'react';
import type { FormEvent } from 'react';
import { Alert, Button, CircularProgress, InputAdornment, Stack, TextField } from '@mui/material';
import type { Credentials } from '../../domain/auth';

interface Props {
  onSubmit: (credentials: Credentials) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}

export function LoginForm({ onSubmit, isSubmitting, error }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!isSubmitting) void onSubmit({ email: email.trim(), password });
  }

  return (
    <Stack component="form" onSubmit={submit} spacing={2.5} aria-busy={isSubmitting}>
      {error && <Alert severity="error" role="alert">{error}</Alert>}
      <TextField id="login-email" name="email" label="Correo electrónico" type="email"
        required autoFocus autoComplete="username" fullWidth disabled={isSubmitting}
        value={email} onChange={(event) => setEmail(event.target.value)} />
      <TextField id="login-password" name="password" label="Contraseña"
        type={showPassword ? 'text' : 'password'} required autoComplete="current-password"
        fullWidth disabled={isSubmitting} value={password}
        onChange={(event) => setPassword(event.target.value)}
        slotProps={{ input: { endAdornment: <InputAdornment position="end">
          <Button type="button" size="small" disabled={isSubmitting}
            aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            aria-pressed={showPassword} onClick={() => setShowPassword((value) => !value)}
            sx={{ minWidth: 64, px: 1 }}>{showPassword ? 'Ocultar' : 'Mostrar'}</Button>
        </InputAdornment> } }} />
      <Button type="submit" variant="contained" fullWidth disabled={isSubmitting}
        startIcon={isSubmitting ? <CircularProgress size={17} color="inherit" /> : undefined}
        sx={{ minHeight: 49 }}>
        {isSubmitting ? 'Ingresando…' : 'Iniciar sesión'}
      </Button>
    </Stack>
  );
}
