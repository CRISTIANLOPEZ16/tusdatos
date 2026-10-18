export interface Session {
  session_id: number;
  event_id: number;
  title: string;
  starts_at: string;
  ends_at: string;
  capacity: number;
  registered_count: number;
  available_capacity: number;
  speaker_names: string[];
}
export interface SessionInput {
  title: string;
  starts_at: string;
  ends_at: string;
  capacity: number;
  speaker_names: string[];
}
export interface SessionPage {
  items: Session[];
  total: number;
  page: number;
  items_per_page: number;
}
export interface Registration {
  event_id: number;
  session_id: number;
  user_id: number;
}
