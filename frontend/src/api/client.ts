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

type RequestContext = {
  method: string;
  normalizedPath: string;
  url: string;
  origin: string;
};

async function handleResponse<T>(response: Response, context: RequestContext): Promise<T> {
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
    const statusLabel = `${response.status}${response.statusText ? ` ${response.statusText}` : ""}`.trim();
    const contextParts = [
      `url=${context.url}`,
      `method=${context.method}`,
      `normalizedPath=${context.normalizedPath}`,
      `API_URL=${API_URL}`,
      `origin=${context.origin}`,
      statusLabel ? `status=${statusLabel}` : null,
      raw ? `response=${raw}` : null,
    ].filter(Boolean);
    throw new Error(`${message} | ${contextParts.join(" | ")}`);
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
  const method = (options.method || "GET").toUpperCase();
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const normalizedPath = normalizeApiPath(path);
  const origin = typeof window !== "undefined" ? window.location.origin : "ssr";
  const url = `${API_URL}${normalizedPath}`;
  let response: Response;
  try {
    response = await fetch(url, {
      credentials: "omit",
      ...options,
      headers,
    });
  } catch (error) {
    const errorMessageParts = [
      "Failed to fetch",
      `method=${method}`,
      `url=${url}`,
      `normalizedPath=${normalizedPath}`,
      `API_URL=${API_URL}`,
      `origin=${origin}`,
    ];
    const cause = error instanceof Error ? error.message : String(error);
    throw new Error(`${errorMessageParts.join(" | ")}${cause ? ` | cause=${cause}` : ""}`);
  }
  if (response.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return request<T>(path, options, false);
    }
    clearTokens();
  }
  return handleResponse<T>(response, { method, normalizedPath, url, origin });
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
