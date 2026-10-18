import type { EventSummary } from '../../domain/event';
import { EventForm } from './EventForm';
import { SessionForm } from '../sessions/SessionForm';
import { useManagementActions } from '../shared/useManagementActions';
export type Editor = { type: 'event'; initial?: EventSummary } | { type: 'session'; event: EventSummary };
export function ManagementDialogs({ editor, onClose, onSaved }: {
  editor: Editor; onClose: () => void; onSaved: (message: string) => void;
}) {
  const actions = useManagementActions();
  if (editor.type === 'event') return <EventForm initial={editor.initial} pending={actions.event.isPending}
    error={actions.event.error?.message ?? ''} onClose={onClose}
    onSubmit={async input => {
      const result = await actions.run(() => actions.event.mutateAsync({ id: editor.initial?.event_id, input }));
      onSaved(`Evento «${result.name}» ${editor.initial ? 'actualizado' : 'creado'}.`);
    }} />;
  return <SessionForm event={editor.event} pending={actions.session.isPending}
    error={actions.session.error?.message ?? ''} onClose={onClose}
    onSubmit={async input => {
      const result = await actions.run(() => actions.session.mutateAsync({ id: editor.event.event_id, input }));
      onSaved(`Sesión «${result.title}» creada.`);
    }} />;
}
