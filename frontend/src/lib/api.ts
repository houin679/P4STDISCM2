const BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://127.0.0.1:8000';

async function refreshAccessToken(): Promise<string | null> {
  try {
    const res = await fetch(`${BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include', // send HttpOnly refresh cookie
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    }
    return null;
  } catch (e) {
    return null;
  }
}

export async function apiFetch(path: string, opts: RequestInit = {}, retry = true): Promise<Response> {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(opts.headers || {});
  if (!headers.has('Content-Type') && !(opts && opts.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const res = await fetch(`${BASE_URL}${path}`, {
    credentials: 'include', // send cookies (refresh token)
    ...opts,
    headers,
  });

  if (res.status === 401 && retry) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers.set('Authorization', `Bearer ${newToken}`);
      return fetch(`${BASE_URL}${path}`, { credentials: 'include', ...opts, headers });
    }
  }

  return res;
}

export async function loginRequest(username: string, password: string) {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);
  const res = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    body,
    credentials: 'include',
  });
  return res;
}

export async function logoutRequest() {
  return fetch(`${BASE_URL}/api/auth/logout`, { method: 'POST', credentials: 'include' });
}

export default { apiFetch, loginRequest, logoutRequest };
