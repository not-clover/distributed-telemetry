# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-05
- **Deciders:** @not-clover

## Context

Two developers in different time zones, one with 2 h/week. Decisions made in a call get lost,
and the absent person needs to understand the "why" asynchronously.

## Decision

We record significant decisions as lightweight ADRs (Michael Nygard format) in `docs/adr/`,
reviewed through PRs like code.

## Consequences

Small writing overhead (~15 min per ADR). In return, new contributors and reviewers can
trace why the system looks the way it does.
