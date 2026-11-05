#!/usr/bin/env bash
# One-shot GitHub setup for CellPulse. Safe to re-run: existing items are skipped.
#
#   ./scripts/github_setup.sh <owner>/<repo> [partner-username]
#
# Requires: gh (logged in with `gh auth login` + `gh auth refresh -s project`) and jq.
# Run it AFTER the first push to main, so the branch ruleset has a branch to protect.
set -euo pipefail

REPO="${1:?usage: github_setup.sh <owner>/<repo> [partner-username]}"
PARTNER="${2:-}"
OWNER="${REPO%%/*}"
ME="$(gh api user --jq .login)"
HERE="$(cd "$(dirname "$0")" && pwd)"
BACKLOG="$HERE/backlog.json"
PROJECT_TITLE="CellPulse Roadmap"

say() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
command -v jq >/dev/null || { echo "jq is required"; exit 1; }

# ---------------------------------------------------------------------------
say "Repository settings"
gh repo edit "$REPO" \
  --description "Distributed telemetry for simulated 5G radio cells: gRPC, Prometheus, Grafana, anomaly detection" \
  --enable-issues --enable-wiki --enable-discussions --enable-projects \
  --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false \
  --enable-auto-merge --delete-branch-on-merge \
  --add-topic 5g --add-topic telemetry --add-topic grpc --add-topic prometheus \
  --add-topic grafana --add-topic distributed-systems --add-topic python --add-topic anomaly-detection
# Squash commit = PR title (so Conventional Commit titles drive the changelog)
gh api -X PATCH "repos/$REPO" -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY >/dev/null
# Let release-please open PRs
gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
# Security features
gh api -X PUT "repos/$REPO/vulnerability-alerts" >/dev/null || true
gh api -X PUT "repos/$REPO/automated-security-fixes" >/dev/null || true
gh api -X PUT "repos/$REPO/private-vulnerability-reporting" >/dev/null || true

# ---------------------------------------------------------------------------
if [[ -n "$PARTNER" ]]; then
  say "Inviting @$PARTNER as collaborator (write access)"
  gh api -X PUT "repos/$REPO/collaborators/$PARTNER" -f permission=push >/dev/null || true
fi

# ---------------------------------------------------------------------------
say "Labels"
label() { gh label create "$1" --color "$2" --description "$3" --repo "$REPO" --force >/dev/null && echo "  $1"; }
for l in "documentation" "duplicate" "enhancement" "invalid" "question" "wontfix" "bug" "help wanted"; do
  gh label delete "$l" --repo "$REPO" --yes >/dev/null 2>&1 || true
done
label "type:story"   "1D76DB" "User-facing feature (user story)"
label "type:task"    "5319E7" "Technical work: infra, CI, docs, refactoring"
label "type:spike"   "FBCA04" "Timeboxed research"
label "type:bug"     "D73A4A" "Something is broken"
label "P0"           "B60205" "Priority: must have for the milestone"
label "P1"           "D93F0B" "Priority: should have"
label "P2"           "FBCA04" "Priority: could have"
label "P3"           "C2E0C6" "Priority: nice to have"
for c in agent collector detector cli api observability infra ci docs; do
  label "component:$c" "BFDADC" "Component: $c"
done
label "owner:partner"            "F9D0C4" "Owned by the partner developer (2 h/week)"
label "good first issue"         "7057FF" "Small, well-scoped, good for onboarding"
label "stretch"                  "EDEDED" "Cut first if the sprint is at risk"
label "icebox"                   "EDEDED" "Not planned in this timebox"
label "status:needs-refinement"  "FEF2C0" "Not ready: needs criteria or estimate"
label "status:needs-triage"      "FEF2C0" "New bug: needs triage"
label "status:blocked"           "000000" "Blocked by something external"
label "post-merge-review"        "C5DEF5" "Merged after 48 h without review; review later"
label "sprint-digest"            "0E8A16" "Weekly automated sprint summary"
label "dependencies"             "0366D6" "Dependency update"

# ---------------------------------------------------------------------------
say "Milestones"
existing_ms="$(gh api "repos/$REPO/milestones?state=all&per_page=100" --jq '.[].title')"
jq -c '.milestones[]' "$BACKLOG" | while read -r m; do
  title="$(jq -r .title <<<"$m")"
  if grep -Fxq "$title" <<<"$existing_ms"; then echo "  exists: $title"; continue; fi
  gh api "repos/$REPO/milestones" -f title="$title" \
    -f description="$(jq -r .description <<<"$m")" \
    -f due_on="$(jq -r .due <<<"$m")T23:59:59Z" >/dev/null
  echo "  created: $title"
done

# ---------------------------------------------------------------------------
say "Project board"
PNUM="$(gh project list --owner "$OWNER" --format json --limit 100 \
  | jq -r --arg t "$PROJECT_TITLE" '.projects[] | select(.title==$t) | .number' | head -1)"
if [[ -z "$PNUM" ]]; then
  PNUM="$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json | jq -r .number)"
  gh project field-create "$PNUM" --owner "$OWNER" --name "Estimate" --data-type NUMBER >/dev/null
  gh project field-create "$PNUM" --owner "$OWNER" --name "Priority" --data-type SINGLE_SELECT \
    --single-select-options "P0,P1,P2,P3" >/dev/null
  gh project field-create "$PNUM" --owner "$OWNER" --name "Component" --data-type SINGLE_SELECT \
    --single-select-options "agent,collector,detector,cli,api,observability,infra,ci,docs" >/dev/null
  echo "  created project #$PNUM"
else
  echo "  exists: project #$PNUM"
fi
gh project link "$PNUM" --owner "$OWNER" --repo "$REPO" >/dev/null 2>&1 || true
gh project edit "$PNUM" --owner "$OWNER" --visibility PUBLIC \
  --description "Sprint board for CellPulse: distributed 5G cell telemetry" >/dev/null || true

PID="$(gh project view "$PNUM" --owner "$OWNER" --format json --jq .id)"
FIELDS="$(gh project field-list "$PNUM" --owner "$OWNER" --format json --limit 50)"
fid()  { jq -r --arg n "$1" '.fields[] | select(.name==$n) | .id' <<<"$FIELDS"; }
oid()  { jq -r --arg n "$1" --arg o "$2" '.fields[] | select(.name==$n) | .options[] | select(.name==$o) | .id' <<<"$FIELDS"; }
EST_F="$(fid Estimate)"; PRI_F="$(fid Priority)"; COMP_F="$(fid Component)"

# ---------------------------------------------------------------------------
say "Issues"
existing_issues="$(gh issue list --repo "$REPO" --state all --limit 500 --json title --jq '.[].title')"
partner_ok=false
if [[ -n "$PARTNER" ]] && gh api "repos/$REPO/collaborators/$PARTNER" >/dev/null 2>&1; then partner_ok=true; fi

jq -c '.issues[]' "$BACKLOG" | while read -r i; do
  title="$(jq -r .title <<<"$i")"
  if grep -Fxq "$title" <<<"$existing_issues"; then echo "  exists: $title"; continue; fi
  type="$(jq -r .type <<<"$i")"; owner="$(jq -r .owner <<<"$i")"
  est="$(jq -r .estimate <<<"$i")"; pri="$(jq -r .priority <<<"$i")"; comp="$(jq -r .component <<<"$i")"
  body="$(jq -r .body <<<"$i")"$'\n\n---\n'"**Estimate:** $est points · **Owner:** $owner"
  labels="type:$type,$pri,component:$comp"
  [[ "$owner" == "partner" ]] && labels+=",owner:partner"
  [[ "$owner" == "partner" && "$type" != "story" ]] && labels+=",good first issue"
  extra="$(jq -r '(.extra_labels // []) | join(",")' <<<"$i")"; [[ -n "$extra" ]] && labels+=",$extra"

  args=(--repo "$REPO" --title "$title" --body "$body" --label "$labels" --milestone "$(jq -r .milestone <<<"$i")")
  if [[ "$owner" == "lead" ]]; then args+=(--assignee "$ME")
  elif $partner_ok; then args+=(--assignee "$PARTNER"); fi

  url="$(gh issue create "${args[@]}")"
  item="$(gh project item-add "$PNUM" --owner "$OWNER" --url "$url" --format json --jq .id)"
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$EST_F" --number "$est" >/dev/null
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$PRI_F" --single-select-option-id "$(oid Priority "$pri")" >/dev/null
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$COMP_F" --single-select-option-id "$(oid Component "$comp")" >/dev/null
  echo "  created: $url"
done

# ---------------------------------------------------------------------------
say "Branch ruleset for main"
if gh api "repos/$REPO/rulesets" --jq '.[].name' | grep -Fxq "Protect main"; then
  echo "  exists"
else
  gh api -X POST "repos/$REPO/rulesets" --input - >/dev/null <<'JSON'
{
  "name": "Protect main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [
          { "context": "Lint & type-check" },
          { "context": "Tests (py3.12)" },
          { "context": "Conventional Commit title" } ] } }
  ]
}
JSON
  echo "  created"
fi

# ---------------------------------------------------------------------------
cat <<EOF

✅ Done. A few things GitHub's API cannot do. Click through these once (≈10 min):

  1. Project board  https://github.com/users/$OWNER/projects/$PNUM
     - Settings → add field 'Sprint' (Iteration, 1 week, start Mon 9 Nov; add Sprint 0 before it)
     - Status field: add options 'Backlog' and 'In review'
     - Views: Board (group by Status), Backlog table (sort by Priority), Roadmap (by Sprint)
     - Workflows: enable 'Auto-add to project' (repo: $REPO), 'Item closed', 'Pull request merged'
  2. Discussions → categories → create 'Standups' (slug: standups) so the stand-up form appears
  3. Wiki tab → 'Create the first page' → Save. Then run the 'Sync wiki' workflow (Actions tab)
  4. Pin the repo on your profile, and pin the Project board to the repo

EOF
