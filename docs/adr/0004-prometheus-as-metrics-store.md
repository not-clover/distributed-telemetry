# 0004. Prometheus as the metrics store

- **Status:** Accepted
- **Date:** 2026-11-05
- **Deciders:** @not-clover

## Context

We need storage, querying and dashboards for time series, with zero custom storage code.

## Decision

Collectors expose received KPIs on `/metrics`; Prometheus scrapes every replica through DNS
service discovery. Grafana and the anomaly detector both query Prometheus.

## Consequences

- Pull model: data resolution is bounded by the scrape interval (5 s). This is acceptable for KPIs.
- Cardinality is `sites × cells × kpis`; at 10k cells we must measure memory (Performance page).
- Long-term retention (Thanos/VictoriaMetrics) is future work.
