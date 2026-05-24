PYTHON ?= python
PYTEST ?= pytest

.PHONY: test-fast release-check

test-fast:
	$(PYTEST) -q \
		tests/test_orbit_status.py \
		tests/test_diagnostic_session.py \
		tests/test_stop_c_approval_gate.py \
		tests/test_validate_orbit_pack.py \
		tests/test_skill_mirror.py \
		tests/test_prompt_assets.py \
		tests/test_skill_catalog.py \
		tests/test_golden_orbit_workflow.py \
		tests/test_codex_review_handoff.py \
		tests/test_skill_integrity.py

release-check:
	$(PYTHON) tools/orbit_repo_audit.py --repo . --out docs/refactor
	$(PYTHON) tools/list_skill_profiles.py --repo . --check
	$(PYTHON) tools/check_skill_mirror.py --repo .
	$(PYTHON) tools/check_prompt_assets.py --repo .
	$(PYTHON) tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all
	$(MAKE) test-fast
