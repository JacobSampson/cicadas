# Approach: Clarify Standardization

## Strategy
Single-threaded: document the standard start flow in one place, then update all entry points (initiative, tweak, bug) to follow it. No partitions—one fix branch implements the whole change.

## Implementation Steps

1. **Canonize the flow** — Add or update a single source of truth for the start flow (e.g. in `SKILL.md`, `EMERGENCE.md`, or a new start-flow doc) with the mandatory sequence:
   - Name → Create draft folder (with initial files) → Requirements source (Q&A, doc, Loom) → Pace (initiatives only: Section, Doc, All) → PR preference (Feature, Initiative, None) → Collect requirements.
   - Rule: pre-populate from user input but always run the flow and verify (e.g. "Name? 1. XYZ, 2. Other").

2. **Wire initiative start** — Update Clarify (and any "start initiative" guidance) so it always runs the standard flow first; create draft folder and `emergence-config.json` (or lifecycle) when applicable before drafting.

3. **Wire tweak start** — Update tweak emergence so it follows the same flow (name, draft folder, PR preference), then collect tweak details.

4. **Wire bug start** — Update bug-fix emergence so it follows the same flow (name, draft folder, PR preference), then collect bug details.

5. **HOW-TO / docs** — Point "Starting work" (or equivalent) in HOW-TO and README at the single flow so Builders and agents have one checklist.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Entry points drift over time | Single documented flow; agents and docs reference it by name/section. |
| Pace/PR options differ by type | Flow explicitly scopes "pace" to initiatives and keeps PR options consistent. |

## Out of Scope
- No change to lifecycle schema or script behavior for PR boundaries; only when/how we ask and in what order.
- No new scripts unless we decide one "start" script that dispatches by type.
