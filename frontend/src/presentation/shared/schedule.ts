const zone = 'America/Bogota';
export function dateLabel(value: string) {
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeZone: zone }).format(new Date(value));
}
export function timeLabel(value: string) {
  return new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23', timeZone: zone }).format(new Date(value));
}
export function scheduleLabel(start: string, end: string) {
  return `${dateLabel(start)} · ${timeLabel(start)} – ${dateLabel(end)} · ${timeLabel(end)}`;
}
export function bogotaInput(value: string) {
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: zone, year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
  }).formatToParts(new Date(value));
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find(p => p.type === type)?.value;
  return `${part('year')}-${part('month')}-${part('day')}T${part('hour')}:${part('minute')}:${part('second')}`;
}
export function bogotaIso(value: string) {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$/.test(value)) throw new Error('Completa las fechas.');
  const iso = `${value}-05:00`;
  if (!Number.isFinite(Date.parse(iso))) throw new Error('La fecha no es válida.');
  return iso;
}
export function validateSchedule(start: string, end: string, bounds?: { starts_at: string; ends_at: string }) {
  if (Date.parse(end) <= Date.parse(start)) throw new Error('La fecha final debe ser posterior a la inicial.');
  if (bounds && (Date.parse(start) < Date.parse(bounds.starts_at) || Date.parse(end) > Date.parse(bounds.ends_at))) {
    throw new Error('La sesión debe quedar dentro del horario del evento.');
  }
}
