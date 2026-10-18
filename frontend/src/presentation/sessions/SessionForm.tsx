import { useState } from 'react';
import type { FormEvent } from 'react';
import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, TextField, Typography } from '@mui/material';
import type { EventSummary } from '../../domain/event';
import type { SessionInput } from '../../domain/session';
import { bogotaInput, bogotaIso, scheduleLabel, validateSchedule } from '../shared/schedule';
export function SessionForm({ event, pending, error, onClose, onSubmit }: {
  event: EventSummary; pending: boolean; error: string; onClose: () => void;
  onSubmit: (input: SessionInput) => Promise<void>;
}) {
  const [validation, setValidation] = useState('');
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (pending) return;
    const data = new FormData(e.currentTarget);
    const text = (key: string) => String(data.get(key) ?? '').trim();
    try {
      const title = text('title');
      if (!title || title.length > 150) throw new Error('El título debe tener entre 1 y 150 caracteres.');
      const starts_at = bogotaIso(text('starts_at')); const ends_at = bogotaIso(text('ends_at'));
      validateSchedule(starts_at, ends_at, event);
      const capacity = Number(text('capacity'));
      if (!Number.isInteger(capacity) || capacity < 1 || capacity > 2147483647) throw new Error('El aforo debe ser un entero entre 1 y 2147483647.');
      const speaker_names = text('speakers').split(/\r?\n/).map(s => s.trim().replace(/\s+/g, ' ')).filter(Boolean);
      if (speaker_names.some(s => s.length > 150)) throw new Error('Cada ponente admite hasta 150 caracteres.');
      if (new Set(speaker_names.map(s => s.toLocaleLowerCase('es-CO'))).size !== speaker_names.length) throw new Error('Los ponentes no pueden repetirse.');
      setValidation('');
      await onSubmit({ title, starts_at, ends_at, capacity, speaker_names });
    } catch (e) { setValidation(e instanceof Error ? e.message : 'Revisa el formulario.'); }
  }
  return <Dialog open fullWidth maxWidth="sm" onClose={() => { if (!pending) onClose(); }} aria-labelledby="session-form-title">
    <DialogTitle id="session-form-title">Agregar nueva sesión</DialogTitle>
    <form onSubmit={submit}>
      <DialogContent><Stack spacing={2.5}>
        <Typography sx={{ fontWeight: 700 }}>{event.name}</Typography>
        <Typography variant="body2" color="text.secondary">Horario del evento: {scheduleLabel(event.starts_at, event.ends_at)} · Bogotá (UTC−5).</Typography>
        {(validation || error) && <Alert severity="error">{validation || error}</Alert>}
        <TextField name="title" label="Título de la sesión" required slotProps={{ htmlInput: { maxLength: 150 } }} />
        <TextField name="starts_at" label="Inicio de la sesión" type="datetime-local" required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: bogotaInput(event.starts_at), max: bogotaInput(event.ends_at), step: 1 } }} />
        <TextField name="ends_at" label="Final de la sesión" type="datetime-local" required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: bogotaInput(event.starts_at), max: bogotaInput(event.ends_at), step: 1 } }} />
        <TextField name="capacity" label="Cupos totales" type="number" required slotProps={{ htmlInput: { min: 1, max: 2147483647, step: 1 } }} />
        <TextField name="speakers" label="Ponentes (opcional)" multiline minRows={3} helperText="Escribe un nombre por línea. No se admiten duplicados." />
      </Stack></DialogContent>
      <DialogActions sx={{ p: 3 }}><Button disabled={pending} onClick={onClose}>Cancelar</Button>
        <Button type="submit" variant="contained" disabled={pending}>{pending ? 'Guardando…' : 'Crear sesión'}</Button>
      </DialogActions>
    </form>
  </Dialog>;
}
