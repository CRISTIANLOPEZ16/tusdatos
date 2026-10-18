import {z} from "zod";
import type { AuthSession } from "../../domain/auth";
import { AppError } from "../../domain/errors";

const claimsSchema = z.object({
    sub: z.string().regex(/^[1-9]\d*$/),
  iat: z.number().int().positive(),
  exp: z.number().int().positive(),
})

export function readJwtSession( accessToken:string, email:string, now = Date.now()): AuthSession{
    try{
        const parts = accessToken.split('.')
        if ( parts.length != 3 || parts.some((part)=> !/^[A-Za-z0-9_-]+$/.test(part))){
            throw new Error('Invalid JWT format')
        }
        const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const binary = atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, '='));
        const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
        const json = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
        const claims = claimsSchema.parse(JSON.parse(json));
        const userId = Number(claims.sub);
        const expiresAt = claims.exp * 1000;
        if (!Number.isSafeInteger(userId) || !Number.isSafeInteger(expiresAt)
        || expiresAt <= now || claims.iat > claims.exp) {
        throw new Error('Invalid or expired claims');
        }
        return { access_token: accessToken, token_type: 'bearer',
        user_id: userId, email, expires_at: expiresAt };
    } catch {
        throw new AppError('La sesión recibida no es válida o ya expiró. Inicia sesión de nuevo.');
    }
}