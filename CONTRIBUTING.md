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
2. **Branch** from `main`: `<type>/<issue-number>-<short-name>`
3. **Commit** using [Conventional Commits](https://www.conventionalcommits.org):
   `feat(collector): stream KPI batches over gRPC`.
4. **Open a PR early** (draft is fine). Fill in the template and write `Closes #12`.
5. **CI must be green.** Request review but PR does not need to wait
6. **Squash-merge.** The PR title becomes the commit on `main` and feeds the changelog.

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`.
Scopes: `agent`, `collector`, `detector`, `api`, `observability`, `deps`, `docs`, `release`.

## Code review agreement

- The author merges once CI is green. 
- Reviews are welcome at any time, including after the merge, label a PR `post-merge-review` if you want a second pair of eyes 

## Changing the API

`proto/` is the contract between all components. Changes need an ADR or an update to ADR-0003,
and both developers must approve. Fields are never renumbered or reused.

## Decisions

Significant technical decisions are written as ADRs in `docs/adr/` (copy `0000-template.md`).

