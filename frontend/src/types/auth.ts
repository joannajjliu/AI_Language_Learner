export interface AuthUser {
  user_id: string;
  email: string;
  name: string;
  picture?: string | null;
}

export interface GoogleAuthResponse {
  user_id: string;
  email: string;
  name: string;
  picture?: string | null;
}
