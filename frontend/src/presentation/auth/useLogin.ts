import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';
import type { Credentials } from '../../domain/auth';
import { AppError } from '../../domain/errors';
import { useAuth } from './useAuth';

export function useLogin() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const request = useRef<AbortController | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => () => { request.current?.abort(); }, []);

  const submit = useCallback(async (credentials: Credentials) => {
    if (request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setError(null);
    setSubmitting(true);
    try {
      await login(credentials, controller.signal);
      if (!controller.signal.aborted) void navigate('/my-dashboard', { replace: true });
    } catch (failure) {
      if (!controller.signal.aborted) {
        setError(failure instanceof AppError ? failure.message : 'No se pudo iniciar sesión. Inténtalo de nuevo.');
      }
    } finally {
      if (request.current === controller) request.current = null;
      if (!controller.signal.aborted) setSubmitting(false);
    }
  }, [login, navigate]);

  return { submit, isSubmitting, error };
}
