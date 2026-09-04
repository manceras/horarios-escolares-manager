import { toApiError } from "@/lib/api/client";

/**
 * Translation keys for a backend error, most specific first.
 *
 * Pass the result straight to `t()`: i18next falls back to the first key of
 * the array that has a translation, landing on `errors.unknown` for any
 * `code` the locale file has not been taught yet. This is the single place
 * that turns a backend error `code` into an i18n key -- `QueryState` and the
 * app-level toast wiring both call it so the mapping never drifts apart.
 */
export function getErrorMessageKeys(error: unknown): [string, string] {
  const { code } = toApiError(error);
  return [`errors.${code}`, "errors.unknown"];
}
