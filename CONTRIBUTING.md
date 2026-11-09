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
5. **CI must be green.** Request review if wanted. 
6. **Squash-merge.** The PR title becomes the commit on `main` and feeds the changelog.

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`.
Scopes: `agent`, `collector`, `detector`, `edge-agent`, `api`, `observability`, `deps`, `docs`,
`release`, `docker`, `main`.

## Code review agreement

- The author merges once CI is green.
- Reviews are welcome at any time if second pair of eyes are needed.

## Changing the API

`proto/` is the contract between all components. Changes need a ADR update.
