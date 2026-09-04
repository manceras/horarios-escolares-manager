import { useState } from "react";

/**
 * One translation key per invalid field, keyed by the field name of `T`.
 * `noUncheckedIndexedAccess` is on, so a lookup like `errors.email` is
 * already typed as `string | undefined` -- exactly what a missing error
 * should look like.
 */
export type FieldErrors<T> = Partial<Record<keyof T, string>>;

export interface EntityFormValidator<T> {
  (values: T): FieldErrors<T>;
}

export interface UseEntityFormResult<T> {
  values: T;
  errors: FieldErrors<T>;
  /** Update one field and clear its error, if any. */
  setField: <K extends keyof T>(field: K, value: T[K]) => void;
  /** Replace all values, e.g. when a create dialog is reopened for editing. */
  setValues: (values: T) => void;
  /** Run `validate` against the current values, store the errors and report whether the form is valid. */
  validate: () => boolean;
  reset: (values: T) => void;
}

/**
 * The shared form pattern for every create/edit dialog: plain controlled
 * state plus a validator function, with no extra dependency. This is enough
 * to give every field a typed value and a typed, per-field error message
 * while staying easy to follow under TypeScript strict mode.
 *
 * `react-hook-form` + `zod` were considered and rejected for this app's
 * small, flat forms -- see the "CRUD screens" section of `frontend/CLAUDE.md`.
 */
export function useEntityForm<T extends object>(
  initialValues: T,
  validate: EntityFormValidator<T>,
): UseEntityFormResult<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<FieldErrors<T>>({});

  function setField<K extends keyof T>(field: K, value: T[K]): void {
    setValues((previous) => ({ ...previous, [field]: value }));
    setErrors((previous) => {
      if (previous[field] === undefined) {
        return previous;
      }
      return { ...previous, [field]: undefined };
    });
  }

  function runValidation(): boolean {
    const nextErrors = validate(values);
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function reset(next: T): void {
    setValues(next);
    setErrors({});
  }

  return { values, errors, setField, setValues, validate: runValidation, reset };
}
