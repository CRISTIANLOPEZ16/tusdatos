import { makeEventHttpAdapter } from '../infrastructure/http/event-http-adapter';
import { getJson } from '../infrastructure/http/http-client';

export const dependencies = { events: makeEventHttpAdapter(getJson) };
