import createClient from "openapi-fetch";

import type { paths } from "./schema";

const TOKEN_STORAGE_KEY = "horarios.accessToken";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

/**
 * Typed API client. Types come from the backend OpenAPI document, so a route
 * change breaks the build instead of breaking at runtime. Run `make gen-api`
 * after touching the API.
 */
export const api = createClient<paths>({ baseUrl: "/" });

api.use({
  onRequest({ request }) {
    const token = getStoredToken();
    if (token) {
      request.headers.set("Authorization", `Bearer ${token}`);
    }
    return request;
  },
});

/** Shape of every error response produced by the backend. */
export interface ApiError {
  detail: string;
  code: string;
}

/**
 * A failed API call. Query hooks throw this so TanStack Query and the UI always
 * receive a real `Error` carrying the backend error `code`.
 */
export class ApiRequestError extends Error implements ApiError {
  readonly code: string;
  readonly detail: string;

  constructor(error: unknown) {
    const { code, detail } = toApiError(error);
    super(detail);
    this.name = "ApiRequestError";
    this.code = code;
    this.detail = detail;
  }
}

/** Narrow an unknown fetch error into something the UI can translate. */
export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiRequestError) {
    return { code: error.code, detail: error.detail };
  }
  if (typeof error === "object" && error !== null && "code" in error && "detail" in error) {
    return { code: String(error.code), detail: String(error.detail) };
  }
  return { detail: "Unexpected error", code: "unknown" };
}
