# Research Posture

ORBIT's default research posture is opportunity-preserving and evidence-bound.

## Default

```yaml
paper_mode: normal
novelty_policy: positioning-first
pre_STOP_A_review_posture: collaborator
post_STOP_C_review_posture: adversarial
concurrent_work_window: 3 months
proposal_stability_after_STOP_A: freeze_by_default
strong_blocker_required_for_abandon: true
```

## Normal Paper Mode

The default goal is a clean, honest, publishable AI paper. A normal paper may be:

- a method combination with clean evidence;
- a controlled empirical finding;
- a reproduction-plus study;
- a benchmark plus strong-baseline package;
- a system paper;
- a focused mechanism paper in a specific regime.

Normal mode does not require a completely new algorithmic breakthrough by default. It
still requires honest claims, reproducible evidence, clear baselines, and no
overclaiming.

## Breakthrough Mode

Breakthrough mode is explicit opt-in only. It raises the bar for method novelty and
allows stronger adversarial review earlier in the process. Do not silently apply
breakthrough-mode standards to a normal-paper workflow.

## Positioning-First Novelty

Similar work is not automatically fatal. Related work should first be classified and used
for positioning. Abandon or reopen the proposal only when a true strong blocker exists.

For every non-strong-blocker, produce at least one viable positioning route, such as:

- narrower regime or task setting;
- stronger evidence, controls, or reproduction;
- different mechanism emphasis;
- benchmark or baseline package;
- reproduction-plus contribution;
- system contribution;
- negative or conditional finding with clear scope.

## Concurrent Work

Work from the last 3 months is concurrent by default. Concurrent work goes to
`orbit-research/CONCURRENT_WORK_WATCHLIST.md`, not directly into proposal rewrites.

Concurrent work may trigger:

- related-work note;
- positioning update;
- future citation;
- optional human decision.

It triggers proposal revision only if novelty-check classifies it as a `STRONG_BLOCKER`
or the user explicitly asks to reopen the proposal.

## Strong Blocker Criteria

A prior work is a `STRONG_BLOCKER` only if it substantially matches all of the following:

1. same problem;
2. same mechanism;
3. same experimental setting;
4. same core claim;
5. reliable evidence;
6. credible baseline/control setup;
7. enough public detail, code, or data to make the claim credible;
8. covers the contribution ORBIT intended to make;
9. leaves no reasonable positioning, stronger-evidence, reproduction-plus, benchmark, or
   regime-based path.

If these are not all substantially true, classify the work as one of:

- `RELATED_BUT_DIFFERENT`
- `CONCURRENT_WORK`
- `WEAK_BLOCKER`
- `POSITIONING_TARGET`
- `REPRODUCTION_TARGET`

## Review Posture

Before STOP A and STOP B, reviewers act as collaborators or paper directors. Their job is
to preserve promising directions, classify risks, propose positioning routes, and identify
the minimum evidence needed for a normal publishable paper.

After STOP C, reviewers act adversarially. Their job is to stress-test paper-level claims,
evidence, baselines, controls, reproducibility, and overclaiming.

## Proposal Stability

After STOP A, `FINAL_PROPOSAL.md` is frozen by default. Do not rewrite it for ordinary
related work. Update the watchlist, related-work notes, or downstream evidence artifacts
instead. Reopen the proposal only for a `STRONG_BLOCKER`, explicit human instruction, or
a result-backed decision recorded in `RESEARCH_DECISION_LOG.md`.
