import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import type { EventPort } from '../../src/application/ports/event-port';
import { Providers } from '../../src/app/providers';
import EventListPage from '../../src/presentation/events/EventListPage';
import { firstPage, later, earlier } from '../fixtures/events';

function mount(events: EventPort, path = '/eventos') {
  return render(<MemoryRouter initialEntries={[path]}>
    <Providers events={events}><EventListPage /></Providers>
  </MemoryRouter>);
}

describe('vista de eventos', () => {
  it('respeta el orden recibido aunque las fechas no sean cronológicas', async () => {
    mount({ list: vi.fn().mockResolvedValue(firstPage) });
    const cards = await screen.findAllByRole('article');
    expect(within(cards[0]).getByRole('heading')).toHaveTextContent(later.name);
    expect(within(cards[1]).getByRole('heading')).toHaveTextContent(earlier.name);
    expect(screen.queryByText(/Ponentes:/)).not.toBeInTheDocument();
    expect(screen.getByText('Mostrando 1–4 de 5 eventos')).toBeVisible();
  });

  it('busca desde página 2 y reinicia a página 1', async () => {
    const user = userEvent.setup();
    const list = vi.fn<EventPort['list']>().mockResolvedValue(firstPage);
    mount({ list }, '/eventos?page=2');
    await screen.findAllByRole('article');
    await user.type(screen.getByRole('textbox', { name: 'Buscar eventos por nombre' }), 'React');
    await user.click(screen.getByRole('button', { name: 'Buscar' }));
    await screen.findByRole('heading', { name: 'Resultados de búsqueda' });
    expect(list).toHaveBeenLastCalledWith({ name: 'React', page: 1, items_per_page: 4 }, expect.any(AbortSignal));
  });

  it('pagina conservando el nombre y permite recuperar una búsqueda vacía', async () => {
    const user = userEvent.setup();
    const list = vi.fn<EventPort['list']>().mockResolvedValue(firstPage);
    mount({ list }, '/eventos?name=React');
    await screen.findAllByRole('article');
    await user.click(screen.getByRole('button', { name: 'Ir a la página 2' }));
    await screen.findAllByRole('article');
    expect(list).toHaveBeenLastCalledWith({ name: 'React', page: 2, items_per_page: 4 }, expect.any(AbortSignal));
    list.mockResolvedValue({ items: [], total: 0, page: 1, items_per_page: 4 });
    const input = screen.getByRole('textbox', { name: 'Buscar eventos por nombre' });
    await user.clear(input);
    await user.type(input, 'No existe{Enter}');
    await screen.findByRole('heading', { name: 'No encontramos eventos' });
    list.mockResolvedValue(firstPage);
    await user.click(screen.getByRole('button', { name: 'Limpiar búsqueda' }));
    await screen.findByRole('heading', { name: 'Eventos' });
  });

  it('avisa que el botón de acceso todavía no autentica', async () => {
    const user = userEvent.setup();
    mount({ list: vi.fn().mockResolvedValue(firstPage) });
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText(/se habilitará en la próxima etapa/)).toBeVisible();
  });

  it('permite recuperar una página que quedó fuera del total', async () => {
    const user = userEvent.setup();
    const list = vi.fn<EventPort['list']>().mockResolvedValue({ ...firstPage, items: [], page: 3 });
    mount({ list }, '/eventos?page=3');
    await screen.findByRole('heading', { name: 'Esta página ya no tiene eventos' });
    await user.click(screen.getByRole('button', { name: 'Ir a la primera página' }));
    expect(list).toHaveBeenLastCalledWith({ name: undefined, page: 1, items_per_page: 4 }, expect.any(AbortSignal));
  });

  it('rechaza un nombre demasiado largo en URL sin consultar la API', async () => {
    const list = vi.fn<EventPort['list']>();
    mount({ list }, `/eventos?name=${'x'.repeat(151)}`);
    expect(await screen.findByText('La búsqueda no puede superar 150 caracteres.')).toBeVisible();
    expect(list).not.toHaveBeenCalled();
  });
});
