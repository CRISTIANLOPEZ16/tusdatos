import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from './useAuth';

export function AuthSessionRedirect() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const previous = useRef(isAuthenticated);
  useEffect(() => {
    const sessionEnded = previous.current && !isAuthenticated;
    previous.current = isAuthenticated;
    if (sessionEnded) void navigate('/eventos', { replace: true });
  }, [isAuthenticated, navigate]);
  return null;
}
