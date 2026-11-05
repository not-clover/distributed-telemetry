# Working Agreement

*Agreed: Sprint 0. Revisited at each retro.*

## Time zones
Sweden CET (UTC+1) · India IST (UTC+5:30), 4.5 h apart. Overlap: **09:00–13:00 CET / 13:30–17:30 IST**.

## Ceremonies
| What | When | Length |
|------|------|--------|
| Planning + review + retro (combined) | Sunday 10:00 CET / 14:30 IST | 30 min |
| Async stand-up (Discussions → Standups) | Mon / Wed / Fri | 2 min |
| Backlog refinement (PO) | Saturday | 30 min |

**Why combined?** One teammate has 2 h/week. Separate Scrum ceremonies would use up
75% of that time, so we compress them and move status updates to async.

## Capacity and estimation
- Fibonacci points; at first, 1 point ≈ 1 focused hour. Re-calibrated after Sprint 1 from real velocity.
- Lead ≈ 10 points/sprint, partner ≈ 1.5 points/sprint + reviews.
- Nothing larger than 5 points enters a sprint.

## Board columns
`Backlog → Todo (this sprint) → In progress → In review → Done`
WIP limit: **2 items in progress per person**.

## Definition of Ready
User-story format · testable acceptance criteria · estimate ≤ 5 · dependencies resolved.

## Definition of Done
- Merged to `main` via a PR with green CI
- Tests for new behaviour; coverage not reduced
- Docs / wiki / ADR updated if relevant
- Acceptance criteria ticked; issue closed by `Closes #N`

## Reviews
Review within 48 h. After that the author may merge with the label `post-merge-review`.

## Communication
- Decisions → ADR or issue comment (never only in chat)
- Urgent → WhatsApp; everything else → GitHub
