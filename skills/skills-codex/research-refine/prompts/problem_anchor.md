---
id: research-refine.problem-anchor.v1
used_by: research-refine phase 0
purpose: Freeze the immutable problem anchor before method invention.
inputs:
  - user research direction
  - optional local grounding material
outputs:
  - problem_anchor
  - non_goals
  - constraints
  - success_condition
---

### Phase 0: Freeze the Problem Anchor

Before proposing anything, extract the user's immutable bottom-line problem. This anchor must be copied verbatim into every proposal and every refinement round.

Write:

- **Bottom-line problem**: What technical problem must be solved?
- **Must-solve bottleneck**: What specific weakness in current methods is unacceptable?
- **Non-goals**: What is explicitly *not* the goal of this project?
- **Constraints**: Compute, data, time, tooling, venue, deployment limits.
- **Success condition**: What evidence would make the user say "yes, this method addresses the actual problem"?

If later reviewer feedback would change the problem being solved, mark that as **drift** and push back or adapt carefully.

**Checkpoint:** Write `refine-logs/REFINE_STATE.json` with `{"phase": "anchor", "round": 0, "agent id": null, "last_score": null, "last_verdict": null, "status": "in_progress", "timestamp": "<now>"}`.
