# frontend/CLAUDE.md

Vite + React 19 + TypeScript (strict) + Tailwind v4 + shadcn/ui + TanStack Query.
Read the root `CLAUDE.md` first.

## Layers

```
src/routes/       one file per URL, composition only
src/features/<x>/ components, hooks and forms of one domain area
src/lib/api/      generated types, typed client, query keys
src/components/ui shadcn/ui primitives (add with the CLI, edit rarely)
src/components/   shared app-level components (QueryState, ...)
src/app/          router, providers, layout
src/locales/      the only place Spanish text is allowed
```

`src/features/teachers/` + `src/routes/TeachersPage.tsx` are the reference
slice. Copy them.

## Non-negotiables

- **No literal user-facing strings.** `t("teachers.title")`, never `"Profesorado"`.
  Add the key to `src/locales/es.json` in the same change.
- **No hand-written API types.** Import from `@/lib/api/schema` (generated) and
  run `make gen-api` after any backend change. Never edit `schema.d.ts`.
- **Server state is TanStack Query only.** No `useEffect` + `fetch`, no global
  store. Query keys come from `@/lib/api/query-keys`.
- **No `any`, no `!`.** Narrow with a check; `strict` and
  `noUncheckedIndexedAccess` are on, so indexed access may be `undefined`.
- Data fetching lives in `src/features/<x>/api.ts`, never inside a component.
- Errors are shown by translating the backend `code`, never by printing
  `detail`. Use `<QueryState />`.
- Imports use the `@/` alias, not `../../..`.
- **There is no login and no current user.** Every route is public: the app runs
  on the user's own machine (ADR 0006). Do not add a guard, a token or a
  "who am I" query.
- **The reader is not technical.** No English fallback text, no error codes on
  screen, no "check the console". Every failure the user can see must be a
  translated sentence that says what to do next.

## Commands

```sh
pnpm install
pnpm dev          # http://localhost:5173, proxies /api to :8000
pnpm typecheck
pnpm lint
pnpm format
pnpm build
pnpm dlx shadcn@latest add table dialog   # add a UI primitive
```

## Styling

Tailwind utilities in the markup. Colors and radii come from the tokens in
`src/index.css` (`bg-background`, `text-muted-foreground`, `border-border`, ...)
-- do not hardcode hex values or arbitrary `[#fff]` classes. Merge conditional
classes with `cn()`.

## Components

Function components, named exports, one component per file, props typed with an
explicit `interface`. Keep a component under ~150 lines; extract instead of
nesting.

## CRUD screens: the shared building blocks

Every data-entry page (teachers, rooms, subjects, class groups, time slots,
curriculum entries) is assembled from the same four pieces. `src/features/teachers/`
+ `src/routes/TeachersPage.tsx` is the reference: list, create, edit, delete
with confirmation, loading/error states and toasts, all built from this.

- **`DataTable<T>`** (`src/components/DataTable.tsx`) -- generic listing table.
  Takes `columns: DataTableColumn<T>[]` (`key`, `header`, `cell: (row: T) => ReactNode`),
  `rows`, `getRowId`, `emptyMessage`, and optional `onEdit` / `onDelete` row
  callbacks that render an actions column. A feature never calls it directly
  in a route -- it wraps it in `<Entity>Table.tsx`, which owns the column
  definitions (see `TeacherTable.tsx`).
- **`EntityDialog`** (`src/components/EntityDialog.tsx`) -- the create/edit
  modal shell. Props: `open`, `onOpenChange`, `title`, optional `description`,
  `children` (the form fields), `onSubmit`, `isSubmitting`, optional `error`
  (a mutation's `error`), optional `submitLabel`. It renders the Cancel/Save
  footer, disables both while `isSubmitting`, and shows the translated error
  banner. It does **not** own the mutation or the open state: call
  `setOpen(false)` from the mutation's `onSuccess` -- that is what "closes on
  success" means in practice.
- **`ConfirmDialog`** (`src/components/ConfirmDialog.tsx`) -- confirmation for
  destructive actions. Same shape as `EntityDialog` minus the form: `open`,
  `onOpenChange`, `title`, `description`, `onConfirm`, `isConfirming`,
  optional `error`. A failed delete (e.g. a 409 because the row is still
  referenced elsewhere) shows its translated message inside the dialog and
  keeps it open, instead of failing silently.
- **`useEntityForm<T>`** (`src/lib/forms/useEntityForm.ts`) -- the form
  pattern: plain controlled state, no extra dependency. `react-hook-form` +
  `zod` were considered and rejected -- these forms are small and flat, and
  plain state already gives typed values and per-field errors under `strict`.
  Reach for a form library only if a future entity genuinely needs schema
  validation, field arrays or async validation, and write an ADR when you do.
  Give it `initialValues: T` and a validator `(values: T) => Partial<Record<keyof T, string>>`;
  it returns `{ values, errors, setField, setValues, validate, reset }`.
  `setField` clears that field's error as you type; `validate()` runs the
  validator, stores the errors and returns whether the form is valid.

Toast feedback is wired once, at the app level, in `src/lib/api/query-client.ts`:
a `MutationCache` shows a translated error toast for every failed mutation and
a success toast for any mutation whose options include
`meta: { successMessageKey: "teachers.createSuccess" }`. A mutation hook that
wants a success toast just adds that `meta` key -- see `useCreateTeacher` in
`src/features/teachers/api.ts`. Both this and `<QueryState />` translate a
backend error the same way, through `getErrorMessageKeys()` in
`src/lib/api/error-translation.ts` -- there is exactly one place that maps an
error `code` to an i18n key.

### Recipe: adding a new CRUD page (e.g. `rooms`)

1. `src/features/rooms/api.ts` -- `useRooms`, `useCreateRoom`, `useUpdateRoom`,
   `useDeleteRoom`, copied from `src/features/teachers/api.ts`. Add
   `meta: { successMessageKey: "rooms.createSuccess" }` (etc.) to each mutation.
   Add `rooms` to `src/lib/api/query-keys.ts`.
2. `src/features/rooms/room-form-values.ts` -- `RoomFormValues`,
   `emptyRoomFormValues`, `validateRoomForm`, copied from
   `teacher-form-values.ts`.
3. `src/features/rooms/RoomForm.tsx` -- the field inputs, taking
   `form: UseEntityFormResult<RoomFormValues>`, copied from `TeacherForm.tsx`.
4. `src/features/rooms/RoomTable.tsx` -- `DataTableColumn<Room>[]` plus
   `<DataTable onEdit onDelete />`, copied from `TeacherTable.tsx`.
5. `src/routes/RoomsPage.tsx` -- composition only: `useRooms` + `<QueryState />`,
   a create button opening an `<EntityDialog>` wrapping `<RoomForm>`, an edit
   `<EntityDialog>` keyed off the row being edited, a `<ConfirmDialog>` for
   delete. Copy `TeachersPage.tsx` and rename.
6. Register the route in `src/app/router.tsx` and the nav entry in
   `src/app/AppLayout.tsx`.
7. Add every string under a `rooms.*` namespace in `src/locales/es.json`,
   reusing the shared `app.*` / `actions.*` / `errors.*` keys instead of
   inventing new ones for "Save", "Cancel", "Edit", "Delete" or error text.

## Shared helpers -- do not rewrite these

Three screens needed the same two functions and three agents wrote them
independently. They now live in exactly one place:

- **`src/lib/weekdays.ts`** -- `day_of_week` is 0 (Monday) to 4 (Friday).
  `weekdayTranslationKey(day)` maps the number to its `app.weekdays.*` key, and
  `dayPeriodKey(day, period)` builds a grid cell lookup key. A raw weekday
  number must never be formatted in a component.
- **`src/lib/time-format.ts`** -- `formatTime("09:00:00")` gives `"09:00"`.
  The API always sends `HH:MM:SS`; the UI always shows `HH:MM`.

Before writing a small helper, grep for it. If two features need it, it belongs
in `src/lib/`.

## i18n key namespaces

- `app.*` -- app-wide chrome and generic words (`app.save`, `app.saving`,
  `app.cancel`, `app.retry`, `app.loading`, `app.yes`, `app.no`).
- `actions.*` -- row/action labels shared by every table (`actions.title`,
  `actions.edit`, `actions.delete`).
- `errors.*` -- one key per backend error `code`, plus `errors.unknown`. Never
  add a page-specific error key here; the backend `code` is already generic.
- `<entity>.*` -- everything specific to one screen: `title`, `empty`,
  `createButton`, `createTitle`, `editTitle`, `deleteTitle`, `deleteConfirm`,
  `createSuccess`, `updateSuccess`, `deleteSuccess`, field labels, and a
  `<entity>.validation.*` sub-namespace for client-side validation messages.
