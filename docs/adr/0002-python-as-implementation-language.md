# 0002. Python as the implementation language

- **Status:** Accepted
- **Date:** 2026-11-05
- **Deciders:** @not-clover, @AnvikaVihaan

## Context

Both developers know Python and C++ from university. The project has a 4-week timebox and
~60 developer-hours in total. Go is the telemetry ecosystem's default language, but neither of
us knows it.

## Options considered

1. **Go**: idiomatic for telemetry, but learning a language would eat the timebox.
2. **C++**: high performance and used in RAN software, but slow to iterate with and a heavy gRPC setup.
3. **Python + asyncio + grpcio**: fastest delivery, and readable for a 2 h/week reviewer.

## Decision

Python 3.12 with `asyncio` and `grpcio`. The protobuf contract stays language-neutral.

## Consequences

- Per-process throughput is lower than Go or C++. We measure it (Performance wiki page) and scale out.
- A C++ agent can be added later against the same `.proto`, which is listed as future work.
