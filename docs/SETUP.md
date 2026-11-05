# First-time setup (≈30 min, once)

You need: Git, Python 3.12+, [GitHub CLI `gh`](https://cli.github.com) and `jq`.
On Windows, run everything in **WSL2** or **Git Bash** (`winget install GitHub.cli jqlang.jq`).

## 1. Put your usernames in

```bash
cd distributed-telemetry
./scripts/personalise.sh <your-github-username> <partner-github-username>
```

## 2. First commit and push (the repo on GitHub is still empty)

```bash
git init -b main
git add .
git commit -m "chore: project scaffold, CI/CD and sprint plan"
git remote add origin https://github.com/<you>/distributed-telemetry.git
git push -u origin main
```

This is the **only** direct push to `main`. After step 3, every change goes through a PR.

## 3. Create labels, milestones, issues, Project board and branch rules

```bash
gh auth login
gh auth refresh -s project          # the Projects API needs this extra scope
./scripts/github_setup.sh <you>/distributed-telemetry <partner-username>
```

The script prints a final checklist of ~10 minutes of clicks that GitHub's API can't do:
the Sprint iteration field, board views, the *Standups* discussion category and the first wiki page.

## 4. Check it worked

- **Actions** tab: CI, CodeQL and Publish image are green on `main`
- **Issues**: 21 issues across 5 milestones
- **Projects**: *CellPulse Roadmap* with Estimate / Priority / Component filled in
- **Packages**: `distributed-telemetry` image on GHCR
- **Wiki**: Home, Onboarding, Working Agreement, Sprint 0 (after you run *Sync wiki*)

## 5. Your partner

1. Accept the collaborator invite (email / GitHub notifications)
2. Follow the wiki page **Onboarding**
3. Her first issue is *Partner onboarding*, labelled `good first issue`

## Daily loop from now on

```bash
git switch -c feat/12-agent-simulator      # branch per issue
# …code… then:
make lint test
git commit -m "feat(agent): simulate diurnal KPI curves"
git push -u origin HEAD
gh pr create --fill --draft                 # write "Closes #12" in the description
```
