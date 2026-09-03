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
src/app/          router, providers, layout, auth guard
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
