import { ManagementContext } from '../../src/presentation/shared/useManagement';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { createAuthDependencies } from '../../src/app/dependencies';
import { AuthProvider } from '../../src/presentation/auth/AuthProvider';
import { RequireAuth } from '../../src/presentation/auth/RequireAuth';
import { AuthSessionRedirect } from '../../src/presentation/auth/AuthSessionRedirect';
import { AuthNavigationButton } from '../../src/presentation/auth/AuthNavigationButton';
import LoginPage from '../../src/presentation/auth/LoginPage';
import MyDashboardPage from '../../src/presentation/profile/MyDashboardPage';
import { theme } from '../../src/presentation/styles/theme';
import { SESSION_KEY } from '../../src/infrastructure/security/session-store';
import { fakeJwt } from '../fixtures/auth';

function CurrentPath() {
  const location = useLocation();
  return <output aria-label="Ruta actual">{location.pathname}</output>;
}

function renderAuth(path = '/login') {
  const queryClient = new QueryClient();
  const runtime = createAuthDependencies(queryClient);
  const management = {
    events: { ...runtime.management.events, mine: async () => ({ items: [], total: 0, page: 1, items_per_page: 6 }) },
    sessions: { ...runtime.management.sessions, mine: async () => ({ items: [], total: 0, page: 1, items_per_page: 5 }) },
  };
  render(<ThemeProvider theme={theme}><CssBaseline />
    <QueryClientProvider client={queryClient}>
      <AuthProvider auth={runtime.auth} sessions={runtime.sessions}
        beforeLogin={runtime.clearPrivateData} endSession={runtime.endSession}>
        <ManagementContext.Provider value={management}><MemoryRouter initialEntries={[path]}><AuthSessionRedirect /><CurrentPath /><Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/eventos" element={<AuthNavigationButton />} />
          <Route path="/eventos/page/:page" element={<AuthNavigationButton />} />
          <Route element={<RequireAuth />}>
            <Route path="/my-dashboard" element={<MyDashboardPage />} />
          </Route>
        </Routes></MemoryRouter></ManagementContext.Provider>
      </AuthProvider>
    </QueryClientProvider>
  </ThemeProvider>);
  return runtime;
}

function seedSession(exp = Math.floor(Date.now() / 1000) + 600) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({
    access_token: fakeJwt({ exp }), token_type: 'bearer', email: 'persona@example.com',
  }));
}

describe('flujo de autenticación', () => {
  it('protege el dashboard cuando se abre directamente sin sesión', async () => {
    renderAuth('/my-dashboard');
    expect(await screen.findByRole('link', { name: 'Iniciar sesión / Registrarse' })).toBeVisible();
    expect(screen.queryByRole('heading', { name: 'Mi dashboard' })).not.toBeInTheDocument();
  });

  it('inicia sesión, persiste y muestra Dashboard al volver a eventos', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ access_token: fakeJwt(), token_type: 'bearer' })));
    renderAuth();
    await user.type(screen.getByLabelText(/Correo electrónico/), 'persona@example.com');
    await user.type(screen.getByLabelText(/^Contraseña/), 'p');
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));
    expect(await screen.findByRole('heading', { name: 'Mi dashboard' })).toBeVisible();
    const stored = JSON.parse(sessionStorage.getItem(SESSION_KEY) ?? '{}');
    expect(stored.email).toBe('persona@example.com');
    expect(stored).not.toHaveProperty('password');
    await user.click(screen.getByRole('link', { name: 'Volver a eventos' }));
    expect(await screen.findByRole('link', { name: 'Dashboard' })).toBeVisible();
    expect(screen.queryByRole('link', { name: 'Iniciar sesión / Registrarse' })).not.toBeInTheDocument();
  });

  it('restaura la sesión guardada y permite entrar al dashboard desde el login', async () => {
    seedSession();
    renderAuth('/login');
    expect(await screen.findByRole('heading', { name: 'Mi dashboard' })).toBeVisible();
    expect(screen.getByText('persona@example.com')).toBeVisible();
  });

  it('muestra credenciales incorrectas sin guardar sesión', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'Invalid' }, { status: 401 })));
    renderAuth();
    await user.type(screen.getByLabelText(/Correo electrónico/), 'persona@example.com');
    await user.type(screen.getByLabelText(/^Contraseña/), 'incorrecta');
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Correo o contraseña incorrectos.');
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
  });

  it('cierra sesión y el guard vuelve al listado', async () => {
    const user = userEvent.setup();
    seedSession();
    renderAuth('/my-dashboard');
    await user.click(await screen.findByRole('button', { name: 'Cerrar sesión' }));
    expect(await screen.findByRole('link', { name: 'Iniciar sesión / Registrarse' })).toBeVisible();
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
  });

  it('401 privado desde otra ruta redirige al listado principal', async () => {
    seedSession();
    const runtime = renderAuth('/eventos/page/2');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'Expired' }, { status: 401 })));
    await act(async () => {
      await expect(runtime.http('/users/me/events')).rejects.toThrow('Tu sesión dejó de estar activa.');
    });
    expect(screen.getByLabelText('Ruta actual')).toHaveTextContent(/^\/eventos$/);
    expect(screen.getByRole('link', { name: 'Iniciar sesión / Registrarse' })).toBeVisible();
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
  });

  it('expira una sesión abierta y retira el dashboard', async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-10-18T15:00:00Z'));
    seedSession(Math.floor(Date.now() / 1000) + 1);
    renderAuth('/my-dashboard');
    expect(screen.getByRole('heading', { name: 'Mi dashboard' })).toBeVisible();
    await act(async () => { await vi.advanceTimersByTimeAsync(1001); });
    expect(screen.getByRole('link', { name: 'Iniciar sesión / Registrarse' })).toBeVisible();
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
  });
});
