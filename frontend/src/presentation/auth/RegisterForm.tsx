import { useState } from 'react';
import type { FormEvent } from 'react';
import { Alert, Button, CircularProgress, InputAdornment, Stack, TextField } from '@mui/material';
import type { Credentials } from '../../domain/auth';
export function RegisterForm({ onSubmit, isSubmitting, error }: {
  onSubmit: (credentials: Credentials) => Promise<void>; isSubmitting: boolean; error: string | null;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [visible, setVisible] = useState(false);
  const [validation, setValidation] = useState('');
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) return;
    if (Array.from(password).length < 8) { setValidation('La contraseña debe tener al menos 8 caracteres.'); return; }
    if (password !== confirmation) { setValidation('Las contraseñas no coinciden.'); return; }
    setValidation('');
    void onSubmit({ email: email.trim(), password });
  }
  return <Stack component="form" spacing={2.5} onSubmit={submit} aria-busy={isSubmitting}>
    {(validation || error) && <Alert severity="error">{validation || error}</Alert>}
    <TextField id="register-email" name="email" label="Correo electrónico" type="email" required autoFocus autoComplete="username" fullWidth
      disabled={isSubmitting} value={email} onChange={event => setEmail(event.target.value)} />
    <TextField id="register-password" name="password" label="Contraseña" type={visible ? 'text' : 'password'} required autoComplete="new-password" fullWidth
      helperText="Usa al menos 8 caracteres." disabled={isSubmitting} value={password} onChange={event => setPassword(event.target.value)}
      slotProps={{ input: { endAdornment: <InputAdornment position="end"><Button type="button" size="small" disabled={isSubmitting}
        aria-label={visible ? 'Ocultar contraseñas' : 'Mostrar contraseñas'} aria-pressed={visible} onClick={() => setVisible(value => !value)}
        sx={{ minWidth: 64, px: 1 }}>{visible ? 'Ocultar' : 'Mostrar'}</Button></InputAdornment> } }} />
    <TextField id="register-confirmation" name="confirmation" label="Confirmar contraseña" type={visible ? 'text' : 'password'} required autoComplete="new-password" fullWidth
      disabled={isSubmitting} value={confirmation} onChange={event => setConfirmation(event.target.value)} />
    <Button type="submit" variant="contained" fullWidth disabled={isSubmitting} sx={{ minHeight: 49 }}
      startIcon={isSubmitting ? <CircularProgress size={17} color="inherit" /> : undefined}>{isSubmitting ? 'Creando cuenta…' : 'Crear cuenta'}</Button>
  </Stack>;
}
