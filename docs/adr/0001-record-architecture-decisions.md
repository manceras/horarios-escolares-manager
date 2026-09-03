# 1. Record architecture decisions

- Status: accepted
- Date: 2026-09-03

## Context

Several agents and people edit this repository. Decisions that are not written
down get silently reversed by whoever comes next.

## Decision

Any decision that constrains future work is recorded here as a short, numbered,
immutable ADR: context, decision, consequences. Superseding an ADR means writing
a new one that says so, not editing the old file.

Write an ADR when you add or drop a dependency, change a layer boundary, pick an
algorithm, or choose a data-model shape that is hard to reverse. Do not write one
for ordinary feature work.

## Consequences

`docs/adr/` is the project's memory. Reading it is part of onboarding, human or
otherwise.
