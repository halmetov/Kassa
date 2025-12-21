import { clearTokens, getAccessToken, refreshAccessToken } from "@/lib/auth";
import { API_URL } from "@/lib/api-url";

const jsonHeaders = {
  "Content-Type": "application/json",
};

function normalizeApiPath(path: string): string {
  if (!path) return path;
  const [pathname, query] = path.split("?");
  const normalizedPath =
    pathname.endsWith("/") && pathname !== "/" ? pathname.replace(/\/+$/, "") : pathname;
  return query ? `${normalizedPath}?${query}` : normalizedPath;
}

async function handleResponse<T>(response: Response): Promise<T> {
  const raw = await response.text();
  let parsed: unknown = null;

  if (raw) {
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = raw;
    }
  }

  if (!response.ok) {
    const detail =
      typeof parsed === "object" && parsed !== null ? (parsed as any).detail || (parsed as any).message : undefined;
    const message = detail || (typeof parsed === "string" ? parsed : raw) || `API error: ${response.status}`;
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T;
  }

  if (!raw) {
    return {} as T;
  }

  return parsed as T;
}

async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const normalizedPath = normalizeApiPath(path);
  const response = await fetch(`${API_URL}${normalizedPath}`, {
    credentials: "omit",
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
