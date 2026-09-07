# 6. Ship as a Windows desktop application, without authentication

Date: 2026-09-07

## Status

Accepted. Supersedes the deployment half of [ADR 0002](0002-stack.md).

## Context

The application was built as a server: a FastAPI process, a separate web client,
Docker Compose, and a login with three roles.

The people who will actually use it are the staff of one primary school, and
one person among them builds the timetable. None of them administer servers.
Every part of the server shape is a task somebody has to do and nobody there
can: find a machine to run it on, keep it patched, hold a password, call
somebody when it stops.

Authentication was protecting the data from nobody. The timetable is made by
one person on one computer; the rest of the staff receive it printed or as a
PDF. A password on a program that only ever runs on its owner's own machine is
a password to forget, and forgetting it is a support call that a Windows account
password already prevents.

## Decision

Ship one Windows program that the user installs and double-clicks.

- **No authentication.** The API binds `127.0.0.1` on a port chosen from
  whatever is free. Nothing off the machine can reach it, and the operating
  system account is the boundary that matters. The `users` table, the roles and
  the JWT are removed rather than disabled.
- **One process.** The API serves the built web client itself, so there is one
  thing to start and one thing to stop.
- **A native window,** through pywebview and the Edge WebView2 runtime that
  Windows 10 and 11 already ship. Where that runtime is missing, the program
  opens the default browser instead of failing.
- **Data in the user profile** (`%LOCALAPPDATA%\Horarios`), never next to the
  executable, with a rotating backup taken on every start and schema migrations
  applied automatically.
- **An installer built by CI on a Windows runner,** because PyInstaller cannot
  cross-compile, published on a tag with the SHA-256 the built-in updater
  verifies before it runs anything.

## Consequences

**The network deployment is gone**, along with `docker-compose.yml` and both
Dockerfiles. Keeping them would have left a public, MIT-licensed repository
containing a one-command way to expose an unauthenticated application holding
staff data to a school network. Anyone who genuinely needs a shared instance has
to put authentication back first, and that is the correct order.

**One computer holds the data.** Two people cannot edit the same timetable, and
a second installation is a second, separate school. This is why the automatic
backups exist and why the data directory is one folder that can be copied.

**Users cannot be added, so a teacher cannot be given read-only access.** If
that is ever wanted, it is a new decision and a new ADR -- and it brings back
the server, not a local login.

**An unsigned installer trips SmartScreen.** Windows shows "Windows protected
your PC" on first run and hides the button behind *More info*. A code-signing
certificate would remove it and costs a few hundred euros a year; until then
this is documented with the exact wording users will see.
