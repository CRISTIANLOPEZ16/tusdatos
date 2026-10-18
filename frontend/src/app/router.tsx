import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router';
import { LinearProgress } from '@mui/material';
import { NotFoundPage } from '../presentation/shared/NotFoundPage';

const EventListPage = lazy(() => import('../presentation/events/EventListPage'));

export function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LinearProgress aria-label="Cargando página" />}>
        <Routes>
          <Route path="/" element={<Navigate to="/eventos" replace />} />
          <Route path="/eventos" element={<EventListPage />} />
          <Route path='eventos/page/:page' element={<EventListPage />} />
          <Route path='eventos/buscar/:name' element={<EventListPage />} />
          <Route path='eventos/buscar/:name/page/:page' element={<EventListPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
