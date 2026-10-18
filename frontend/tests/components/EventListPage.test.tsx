import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router';
import type { EventPort } from '../../src/application/ports/event-port';
import { Providers } from '../../src/app/providers';
import EventListPage from '../../src/presentation/events/EventListPage';
import { firstPage, later, earlier } from '../fixtures/events';

function mount(events: EventPort, path = '/eventos') {
  return render(<MemoryRouter initialEntries={[path]}>
    <Providers events={events}><Routes>
      <Route path="/eventos" element={<EventListPage />} />
      <Route path="/eventos/page/:page" element={<EventListPage />} />
      <Route path="/eventos/buscar/:name" element={<EventListPage />} />
      <Route path="/eventos/buscar/:name/page/:page" element={<EventListPage />} />
    </Routes></Providers>
  </MemoryRouter>);
}

describe('vista de eventos', () => {
  it('respeta el orden recibido aunque las fechas no sean cronológicas', async () => {
    mount({ list: vi.fn().mockResolvedValue(firstPage) });
    const cards = await screen.findAllByRole('article');
    expect(within(cards[0]).getByRole('heading')).toHaveTextContent(later.name);
    expect(within(cards[1]).getByRole('heading')).toHaveTextContent(earlier.name);
    expect(screen.getByText('Mostrando 1–4 de 5 eventos')).toBeVisible();
  });

  it('busca desde otra página, vuelve a la primera y conserva el filtro al paginar', async () => {
    const user = userEvent.setup();
    const list = vi.fn<EventPort['list']>().mockResolvedValue(firstPage);
    mount({ list }, '/eventos/page/2');
    await screen.findAllByRole('article');
    await user.type(screen.getByRole('textbox', { name: 'Buscar eventos por nombre' }), 'React');
    await user.click(screen.getByRole('button', { name: 'Buscar' }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(
      { name: 'React', page: 1, items_per_page: 4 }, expect.any(AbortSignal),
    ));
    await user.click(screen.getByRole('button', { name: 'Ir a la página 2' }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(
      { name: 'React', page: 2, items_per_page: 4 }, expect.any(AbortSignal),
    ));
  });
});
