import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Providers } from './providers';
import { AppRouter } from './router';

const root = document.getElementById('root');
if (!root) throw new Error('Falta el elemento raíz de la aplicación.');

createRoot(root).render(
  <StrictMode><Providers><AppRouter /></Providers></StrictMode>,
);
