import { createContext, useContext } from 'react';
import type { RegistrationPort } from '../../application/ports/registration-port';
export const RegistrationContext = createContext<RegistrationPort | null>(null);
export function useRegistration() {
  const port = useContext(RegistrationContext);
  if (!port) throw new Error('Falta RegistrationContext.');
  return port;
}
