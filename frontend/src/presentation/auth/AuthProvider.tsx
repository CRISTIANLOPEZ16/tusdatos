import { useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';
import type { PropsWithChildren } from 'react';
import type { AuthPort, SessionStorePort } from '../../application/ports/auth-port';
import type { Credentials } from '../../domain/auth';
import { AuthContext } from './useAuth';

type Props = PropsWithChildren<{
  auth: AuthPort;
  sessions: SessionStorePort;
  beforeLogin: () => void;
  endSession: () => void;
}>;

export function AuthProvider({ children, auth, sessions, beforeLogin, endSession }: Props) {
  const session = useSyncExternalStore(sessions.subscribe, sessions.getSnapshot, () => null);
  const attempt = useRef(0);

  const login = useCallback(async (credentials: Credentials, signal?: AbortSignal) => {
    const currentAttempt = ++attempt.current;
    const next = await auth.login(credentials, signal);
    if (signal?.aborted || currentAttempt !== attempt.current) {
      throw new DOMException('Inicio de sesión cancelado.', 'AbortError');
    }
    beforeLogin();
    sessions.set(next);
  }, [auth, sessions, beforeLogin]);

  const logout = useCallback(() => {
    ++attempt.current;
    endSession();
  }, [endSession]);

  useEffect(() => {
    if (!session) return;
    const activeSession = session;
    let timer: number | undefined;
    function checkExpiration() {
      window.clearTimeout(timer);
      if (sessions.getSnapshot()?.access_token !== activeSession.access_token) return;
      const remaining = activeSession.expires_at - Date.now();
      if (remaining <= 0) {
        logout();
      } else {
        timer = window.setTimeout(checkExpiration, Math.min(remaining, 2_147_483_647));
      }
    }
    function onVisibility() {
      if (document.visibilityState === 'visible') checkExpiration();
    }
    checkExpiration();
    window.addEventListener('focus', checkExpiration);
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener('focus', checkExpiration);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [session, sessions, logout]);

  const value = useMemo(() => ({
    isAuthenticated: session !== null,
    user: session ? { user_id: session.user_id, email: session.email } : null,
    login, logout,
  }), [session, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
