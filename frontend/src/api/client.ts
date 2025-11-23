import { clearTokens, getAccessToken, refreshAccessToken } from "@/lib/auth";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const jsonHeaders = {
  "Content-Type": "application/json",
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API error: ${response.status}`);
  }
  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
}

async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    ...options,
    headers,
  });
  if (response.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return request<T>(path, options, false);
    }
    clearTokens();
  }
  return handleResponse<T>(response);
}

export async function apiGet<T>(path: string, options: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "GET",
    ...options,
  });
}

export async function apiPost<T>(path: string, body: unknown, options: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { ...jsonHeaders, ...(options.headers || {}) },
    body: JSON.stringify(body),
    ...options,
  });
}

export async function apiPut<T>(path: string, body: unknown, options: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "PUT",
    headers: { ...jsonHeaders, ...(options.headers || {}) },
    body: JSON.stringify(body),
    ...options,
  });
}

export async function apiUpload<T>(path: string, formData: FormData, options: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: formData,
    ...options,
  });
}

export async function apiDelete<T>(path: string, options: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "DELETE",
    ...options,
  });
}

export { API_URL };
