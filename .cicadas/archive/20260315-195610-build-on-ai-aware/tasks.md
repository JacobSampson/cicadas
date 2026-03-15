# Tasks: build-on-ai-aware

## Partition: feat/start-flow-config

- [x] Update `emergence/start-flow.md`: add step "Building on AI? (yes/no)" after Create draft folder, before Requirements source (initiatives) or PR preference (tweaks/bugs) <!-- id: 1 -->
- [x] Add exact copy for gate and eval-status questions per UX (gate: "Is this project building on AI? (yes / no)"; eval status: "Does this project already have completed evals, or will you be doing evals? (already have / will do)") <!-- id: 2 -->
- [x] Document in start-flow that agent writes `building_on_ai` and `eval_status` to `emergence-config.json` in draft folder, merging with existing keys <!-- id: 3 -->
- [x] Verify clarify.md, tweak.md, bug-fix.md reference start flow and that new step runs for initiative, tweak, and bug <!-- id: 4 -->
- [ ] Reflect: update this tasks.md and any active specs if implementation diverged <!-- id: 5 -->
- [ ] Open PR: feat/start-flow-config → initiative/build-on-ai-aware <!-- id: 6 -->

---

## Partition: feat/approach-eval-step

- [x] Update `emergence/approach.md`: add step after Ingest to read `emergence-config.json` from drafts (or active) for the initiative <!-- id: 10 -->
- [ ] If `building_on_ai` and `eval_status == "will_do"`, add prompt: ask placement (before / parallel) with exact UX copy <!-- id: 11 -->
- [x] When user chooses parallel, show warning and suggestion to wait per UX <!-- id: 12 -->
- [x] Document writing `eval_placement` ("before_build" | "parallel") to emergence-config.json <!-- id: 13 -->
- [x] When drafting approach.md, if eval placement set, add explicit "Eval" step in sequence with wording for before_build vs parallel <!-- id: 14 -->
- [ ] Reflect: update tasks.md and active specs if diverged <!-- id: 15 -->
- [ ] Open PR: feat/approach-eval-step → initiative/build-on-ai-aware <!-- id: 16 -->

---

## Partition: feat/eval-spec-and-reminders

- [x] Add `templates/eval-spec.md` with structure from reqt-template (problem, use case, hypothesis, scope, success criteria, metrics, data, methodology, model/resources, harness, timeline, results, exit criteria, wrap-up) <!-- id: 20 -->
- [x] Add `emergence/eval-spec.md`: when to run (initiatives, after PRD/UX/Tech, eval_status will_do, user accepted); template and playbook paths; output path; six-step playbook summary <!-- id: 21 -->
- [x] Update `emergence/tweak.md`: when drafting tweaklet, if building_on_ai and eval_status will_do, offer eval/benchmark reminder per UX copy; do not offer full eval spec <!-- id: 22 -->
- [x] Update `emergence/bug-fix.md`: when drafting buglet, same as tweak — offer reminder per UX; no full eval spec <!-- id: 23 -->
- [ ] Reflect: update tasks.md and active specs if diverged <!-- id: 24 -->
- [ ] Open PR: feat/eval-spec-and-reminders → initiative/build-on-ai-aware <!-- id: 25 -->

---

## Partition: feat/docs

- [x] Update SKILL.md: add Building on AI flow (gate, eval status, eval spec offer, placement, tweak/bug reminder); reference emergence-config keys <!-- id: 30 -->
- [x] Update HOW-TO.md and/or README if they describe emergence or start flow; add note on Building on AI and evals <!-- id: 31 -->
- [x] Update CLAUDE.md or implementation.md if they reference start flow or emergence <!-- id: 32 -->
- [x] Verify consistency-check or other docs are aware of optional eval-spec.md <!-- id: 33 -->
- [ ] Reflect: update tasks.md and active specs if diverged <!-- id: 34 -->
- [ ] Open PR: feat/docs → initiative/build-on-ai-aware <!-- id: 35 -->

---

## Completion (after all partitions merged)

- [ ] Merge initiative/build-on-ai-aware to master (per lifecycle) <!-- id: 40 -->
- [ ] Synthesize canon on master; archive specs <!-- id: 41 -->
