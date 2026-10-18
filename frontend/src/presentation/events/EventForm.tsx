import { useState } from 'react';
import type { FormEvent } from 'react';
import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Typography } from '@mui/material';
import type { EventInput, EventSummary } from '../../domain/event';
import { bogotaInput, bogotaIso, validateSchedule } from '../shared/schedule';
export function EventForm({ initial, pending, error, onClose, onSubmit }: {
  initial?: EventSummary; pending: boolean; error: string; onClose: () => void;
  onSubmit: (input: EventInput) => Promise<void>;
}) {
  const [validation, setValidation] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const data = new FormData(event.currentTarget);
    const text = (key: string) => String(data.get(key) ?? '').trim();
    try {
      const starts_at = bogotaIso(text('starts_at'));
      const ends_at = bogotaIso(text('ends_at'));
      validateSchedule(starts_at, ends_at);
      const name = text('name'); const address = text('address');
      if (name.length < 3 || name.length > 150 || address.length < 5 || address.length > 150) throw new Error('Revisa el nombre y la dirección.');
      const status = text('status');
      if (!['activo', 'borrador', 'cancelado', 'finalizado', 'archivado'].includes(status)) throw new Error('Estado inválido.');
      setValidation('');
      await onSubmit({ name, address, description: text('description') || null, starts_at, ends_at, status: status as EventInput['status'] });
    } catch (e) { setValidation(e instanceof Error ? e.message : 'Revisa el formulario.'); }
  }
  return <Dialog open fullWidth maxWidth="sm" onClose={() => { if (!pending) onClose(); }} aria-labelledby="event-form-title">
    <DialogTitle id="event-form-title">{initial ? 'Editar evento' : 'Crear evento'}</DialogTitle>
    <form onSubmit={submit}>
      <DialogContent><Stack spacing={2.5}>
        {(validation || error) && <Alert severity="error">{validation || error}</Alert>}
        <TextField name="name" label="Nombre del evento" required defaultValue={initial?.name ?? ''} slotProps={{ htmlInput: { minLength: 3, maxLength: 150 } }} />
        <TextField name="description" label="Descripción (opcional)" multiline minRows={3} defaultValue={initial?.description ?? ''} />
        <TextField name="address" label="Dirección" required defaultValue={initial?.address ?? ''} slotProps={{ htmlInput: { minLength: 5, maxLength: 150 } }} />
        <Typography variant="body2" color="text.secondary">Todas las fechas y horas corresponden a Bogotá (UTC−5).</Typography>
        <TextField name="starts_at" label="Inicio" type="datetime-local" required defaultValue={initial ? bogotaInput(initial.starts_at) : ''} slotProps={{ inputLabel: { shrink: true }, htmlInput: { step: 1 } }} />
        <TextField name="ends_at" label="Finalización" type="datetime-local" required defaultValue={initial ? bogotaInput(initial.ends_at) : ''} slotProps={{ inputLabel: { shrink: true }, htmlInput: { step: 1 } }} />
        <TextField name="status" label="Estado" select defaultValue={initial?.status ?? 'activo'}>
          {['activo', 'borrador', 'cancelado', 'finalizado', 'archivado'].map(value => <MenuItem key={value} value={value}>{value}</MenuItem>)}
        </TextField>
      </Stack></DialogContent>
      <DialogActions sx={{ p: 3 }}><Button onClick={onClose} disabled={pending}>Cancelar</Button>
        <Button type="submit" variant="contained" disabled={pending}>{pending ? 'Guardando…' : initial ? 'Guardar cambios' : 'Crear evento'}</Button>
      </DialogActions>
    </form>
  </Dialog>;
}
