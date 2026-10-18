import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router';
import { LinearProgress } from '@mui/material';
import { NotFoundPage } from '../presentation/shared/NotFoundPage';
import { RequireAuth } from '../presentation/auth/RequireAuth';
import { AuthSessionRedirect } from '../presentation/auth/AuthSessionRedirect';

const EventListPage = lazy(() => import('../presentation/events/EventListPage'));
const LoginPage = lazy(() => import('../presentation/auth/LoginPage'));
const MyDashboardPage = lazy(() => import('../presentation/profile/MyDashboardPage'));

const EventDetailPage = lazy(() => import('../presentation/events/EventDetailPage'));

export function AppRouter() {
  return (
    <BrowserRouter>
      <AuthSessionRedirect />
      <Suspense fallback={<LinearProgress aria-label="Cargando página" />}>
        <Routes>
          <Route path="/" element={<Navigate to="/eventos" replace />} />
          <Route path="/eventos" element={<EventListPage />} />
          <Route path="/eventos/page/:page" element={<EventListPage />} />
          <Route path="/eventos/buscar/:name" element={<EventListPage />} />
          <Route path="/eventos/buscar/:name/page/:page" element={<EventListPage />} />
          <Route path="/eventos/:eventId" element={<EventDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RequireAuth />}>
            <Route path="/my-dashboard" element={<MyDashboardPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
