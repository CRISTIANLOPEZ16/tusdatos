import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import type { Credentials } from '../../domain/auth';
import { AppError } from '../../domain/errors';
import { useRegistration } from './useRegistration';
export function useRegister() {
  const registration = useRegistration();
  const navigate = useNavigate();
  const request = useRef<AbortController | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => () => { request.current?.abort(); }, []);
  async function submit(credentials: Credentials) {
    if (request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setError(null); setSubmitting(true);
    try {
      await registration.register(credentials, controller.signal);
      if (!controller.signal.aborted) void navigate('/login', { replace: true, state: { registered: true } });
    } catch (failure) {
      if (!controller.signal.aborted) setError(failure instanceof AppError ? failure.message : 'No pudimos crear la cuenta. Inténtalo de nuevo.');
    } finally {
      if (request.current === controller) request.current = null;
      if (!controller.signal.aborted) setSubmitting(false);
    }
  }
  return { submit, isSubmitting, error };
}
