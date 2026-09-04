# Security policy

## Supported versions

This project is pre-1.0. Only the `main` branch receives security fixes.

## Reporting a vulnerability

Please do **not** open a public issue. Use GitHub's
[private vulnerability reporting](https://github.com/manceras/horarios-escolares-manager/security/advisories/new)
so the problem can be fixed before it is disclosed.

Include what you found, how to reproduce it, and what an attacker could do with
it. You will get an acknowledgement within a few days.

## Scope notes for self-hosters

This application stores personal data about teachers and pupils' groups. If you
deploy it in a school:

- set a long random `SECRET_KEY`; the default value in `.env.example` is not one
- serve it over HTTPS — access tokens travel in the `Authorization` header
- restrict access to the SQLite volume and back it up somewhere encrypted
- never run `make seed` against a real school: it inserts sample data and
  accounts whose password is public. Create the first account with
  `make create-user`, which prompts for a password of at least 12 characters
