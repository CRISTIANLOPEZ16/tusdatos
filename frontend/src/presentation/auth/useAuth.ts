import {createContext, useContext } from 'react';
import type { Credentials } from '../../domain/auth';
interface AuthContextValue {
    isAuthenticated: boolean;
    user:{user_id: number; email:string;} | null;
    login(credentials: Credentials, signal:AbortSignal): Promise<void>;
    logout():void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(){
    const context = useContext(AuthContext);
    if (!context) throw new Error('Falta AuthProvider.');
    return context;
}