# Security policy

## Supported versions

This project is pre-1.0. Only the `main` branch receives security fixes.

## Reporting a vulnerability

Please do **not** open a public issue. Use GitHub's
[private vulnerability reporting](https://github.com/manceras/horarios-escolares-manager/security/advisories/new)
so the problem can be fixed before it is disclosed.

Include what you found, how to reproduce it, and what an attacker could do with
it. You will get an acknowledgement within a few days.

## The security model

This is a desktop application with **no authentication**, by design — see
[ADR 0006](docs/adr/0006-desktop-application.md). One person builds the school's
timetable on their own computer; the Windows account they log into is the
boundary. The API binds `127.0.0.1` on a port chosen at startup, so nothing off
that machine can reach it.

Two things follow, and they matter:

- **Never bind this application to a non-loopback interface.** Running
  `uvicorn app.main:app --host 0.0.0.0` hands anyone on the school's network
  read and write access to staff data. `docker-compose.yml` and the Dockerfiles
  were removed for exactly this reason. If you want a shared instance, put
  authentication back first.
- **Never run `make seed` against a real school.** It inserts a fictional
  6-group school and will interleave it with real data.

It stores personal data about teachers and the groups they teach. The database
lives unencrypted in the user profile (`%LOCALAPPDATA%\Horarios`), so it is
protected by the machine's disk encryption and account password and by nothing
else. On a shared or unencrypted computer, that is worth knowing before real
staff data goes in.

## Updates

The application checks GitHub for new releases and can install them. Each
download is verified against the SHA-256 published with the release before it is
run, and a mismatch aborts the update. The installer itself is **not
code-signed**, which is why Windows warns about it on first run.
