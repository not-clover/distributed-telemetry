# Contributing to CellPulse

## Getting started

```bash
make dev    # Python 3.12+ venv, deps, generated protobuf code, pre-commit hooks
make test
make lint
```

## Workflow (trunk-based)

1. **Pick an issue** from the current sprint column on the Project board and assign yourself.
   Move it to *In progress*.
2. **Branch** from `main`: `<type>/<issue-number>-<short-name>`, e.g. `feat/12-collector-ingest`.
3. **Commit** using [Conventional Commits](https://www.conventionalcommits.org):
   `feat(collector): stream KPI batches over gRPC`.
4. **Open a PR early** (draft is fine). Fill in the template and write `Closes #12`.
5. **CI must be green.** Request review; CODEOWNERS adds reviewers automatically.
6. **Squash-merge.** The PR title becomes the commit on `main` and feeds the changelog.

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`.
Scopes: `agent`, `collector`, `detector`, `cli`, `api`, `observability`, `deps`, `docs`, `release`.

## Code review agreement

- Review within **48 hours** of the request. If there is no review by then, the author may merge
  and add the label `post-merge-review`, and the reviewer looks at it in their next session.
- Keep PRs under ~400 changed lines. Small PRs get reviewed; big ones get skimmed.
- Comment prefixes: `nit:` (optional), `question:`, `suggestion:`, `blocking:`.
- Approve when it is better than `main` and has no `blocking:` comments. Perfection is not the bar.

## Changing the API

`proto/` is the contract between all components. Changes need an ADR or an update to ADR-0003,
and both developers must approve. Fields are never renumbered or reused.

## Decisions

Significant technical decisions are written as ADRs in `docs/adr/` (copy `0000-template.md`).

## Async stand-ups

Mon / Wed / Fri in Discussions → *Standups*: what you did, what you'll do next, and any blockers.
It takes two minutes and replaces a daily meeting across our 4.5-hour time difference.
