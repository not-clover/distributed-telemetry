# 0003. gRPC client-streaming with a versioned protobuf contract

- **Status:** Proposed (partner review in Sprint 0)
- **Date:** 2026-11-05
- **Deciders:** @not-clover, @AnvikaVihaan

## Context

Agents send small KPI batches every second, indefinitely. We need a typed, compact,
evolvable wire format and a connection model that copes with collector restarts.

## Options considered

1. **HTTP/JSON POST per batch**: simple, but verbose, untyped and with per-request overhead.
2. **Message broker (Kafka/NATS)**: robust, but adds infrastructure beyond the timebox.
3. **gRPC client-streaming (`stream KpiBatch → StreamSummary`)**: one long-lived HTTP/2 stream per agent, typed schema, generated stubs.

## Decision

Option 3. Package `cellpulse.v1`. Each batch carries `site_id` and a monotonic `sequence`
so collectors can detect gaps and duplicates after reconnects.

## Consequences

- Client-side `round_robin` load balancing over DNS spreads agents across collectors (see v0.2).
- Breaking changes require `cellpulse.v2`; field numbers are never reused.
- A broker remains a documented future option if we need replay or fan-out.
