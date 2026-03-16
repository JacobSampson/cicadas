---
name: test-coverage-review
description: Reviews existing test suites for coverage gaps, quality, and rigor; identifies weak or missing tests and guides fixes to reach a target coverage threshold. Use when asked to "review unit tests", "fix unit tests", "check test coverage", "audit tests", "improve test suite", or ensure coverage at end of an initiative or during maintenance. Do NOT use when the user asks to write tests from scratch for new, untested code.
license: Apache-2.0
---

# Test Coverage Review

## Goal

Audit the existing test suite, identify gaps and weak tests, and guide fixes until the suite provides robust, working coverage — typically to a Builder-specified threshold (e.g. "ensure 80% coverage").

## Process

1. **Discover the test harness** — detect the host language and test framework (e.g. Python/unittest, JS/Jest, Go/testing). Identify how to run tests and generate a coverage report. If unclear, ask the Builder before proceeding.
2. **Run tests + coverage** — execute the suite and capture the coverage report. Surface any failing tests immediately; do not proceed past failures without Builder acknowledgment.
3. **Read source code** — understand the intended behaviors of each module under review.
4. **Cross-reference tests against source** — for each public function, method, or behavior, check whether it has meaningful test coverage.
5. **Apply the gap checklist** (see below).
6. **Emit a structured findings report** (see Feedback Format).
7. **Fix or guide fixes** — for each CRITICAL or GAP finding, either fix the test directly (if unambiguous) or describe exactly what needs to change and why.

## Review Dimensions

| Dimension | What to assess |
|-----------|----------------|
| **Behavioral coverage** | Are all meaningful behaviors tested — not just the happy path? |
| **Boundary & edge cases** | Min/max values, empty inputs, single-element collections, off-by-one |
| **Error & failure paths** | Invalid inputs, missing resources, external failures, permission errors |
| **Integration points** | Interactions between components, I/O side effects, state changes |

Line/branch coverage metrics are supporting evidence — not the goal. A test that touches a line without asserting a meaningful outcome provides false confidence.

## Quality Signals

### Assertions
- Must be **specific**: prefer `assertEqual(result, expected)` over `assertIsNotNone(result)`
- Tests with no assertions, or only presence checks, are weak
- Each test should assert **one logical outcome** (multiple related assertions in one test are fine; testing multiple unrelated behaviors is not)

### Mocks
- **Minimize mocks.** Mocks verify calling convention, not that the system actually works. A suite dominated by mocks can pass 100% while hiding real integration bugs.
- Prefer real implementations on temp state (temp dirs, in-memory DBs, local git repos) over mocking the I/O layer
- Mocks are appropriate only for: pure logic with no I/O, external services that cannot be stood up locally, or deliberately isolating a unit when the real dependency is prohibitively slow
- Flag tests that mock the return value of the function under test — these provide zero coverage

### Test isolation
- Tests must not depend on execution order
- Global or shared state must be reset in setup/teardown
- File system or network I/O must use temp directories or fixtures, not production paths

### Naming
- Test names must describe the scenario and expected outcome, not just the method name
  - ✅ `test_archive_raises_when_registry_missing`
  - ❌ `test_archive_2`

### Flakiness risks
- Time-dependent logic without a clock injection point
- Random values without a seed
- Race conditions in async code

## Common Gap Checklist

1. **Empty / null / None inputs** — especially for functions accepting collections or strings
2. **Repeated operations** — does calling something twice break idempotent behavior?
3. **Partial failure** — first step of a multi-step operation succeeds but second fails
4. **Sequential state** — tests verify only final state and miss intermediate corruption
5. **Error message content** — tests only check an exception is raised, not what it says
6. **Side effects** — functions that write files, mutate state, or emit events tested for return value only

## Feedback Format

Group findings by severity:

- **CRITICAL** — missing coverage of a core behavior or entire failure mode
- **GAP** — existing test is too weak to catch real regressions (vacuous assertion, missing edge case)
- **SUGGESTION** — test could be cleaner or more precise; low risk

For each finding:
```
[SEVERITY] <file>: <test name or untested function>
Why it matters: <one sentence>
What to add/fix: <concrete, actionable suggestion>
```

Conclude with: current coverage %, target coverage %, and a prioritized fix list.

## Notes

- Always check for project-specific test conventions in `CLAUDE.md`, `AGENTS.md`, or a `CONTRIBUTING.md` at the repo root before starting — some projects enforce real-filesystem tests, ban mocks entirely, or use non-standard runners.
- If the Builder has not stated a target coverage threshold, ask before proceeding.
