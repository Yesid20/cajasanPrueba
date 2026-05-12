
export type Tokens = {
  accessToken: string;
  refreshToken: string;
  expiresIn: number; 
};

let accessToken: string | null = null;
let refreshToken: string | null = null;
let accessExpiresAt: number | null = null;

export function setTokens(tokens: Tokens) {
  accessToken = tokens.accessToken;
  refreshToken = tokens.refreshToken;
  accessExpiresAt = Date.now() + tokens.expiresIn * 1000;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getRefreshToken(): string | null {
  return refreshToken;
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  accessExpiresAt = null;
}

export function isAccessExpired(): boolean {
  if (!accessExpiresAt) return true;
  return Date.now() >= accessExpiresAt;
}
