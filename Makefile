PYTHON ?= python
PYTEST ?= pytest

TEST_CORE_FILES := \
	tests/test_orbit_status.py \
	tests/test_diagnostic_session.py \
	tests/test_stop_c_approval_gate.py \
	tests/test_validate_orbit_pack.py \
	tests/test_codex_review_handoff.py

.PHONY: test-core test-cli test-static test-fast release-check

test-core:
	$(PYTEST) -q $(TEST_CORE_FILES) -k "not cli"

test-cli:
	$(PYTHON) tools/orbit_status.py --repo tests/fixtures/golden_minimal_project --json >/dev/null
	$(PYTHON) tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all
	$(PYTHON) tools/check_stop_c_approval.py --repo tests/fixtures/golden_minimal_project --claim-ledger claims/claim_ledger.json --json >/dev/null
	$(PYTHON) tools/codex_review_handoff.py --help >/dev/null
	tmpdir=$$(mktemp -d); \
	$(PYTHON) tools/diagnostic_session.py create --repo "$$tmpdir" --input "python train.py --smoke" --json >/dev/null; \
	rm -rf "$$tmpdir"

test-static:
	$(PYTHON) tools/check_skill_mirror.py --repo .
	$(PYTHON) tools/check_prompt_assets.py --repo .
	$(PYTHON) tools/list_skill_profiles.py --repo . --check
	$(PYTEST) -q \
		tests/test_skill_mirror.py \
		tests/test_skill_integrity.py \
		-k "not install"

test-fast:
	$(MAKE) test-core
	$(MAKE) test-cli
	$(MAKE) test-static

release-check:
	$(PYTHON) tools/orbit_repo_audit.py --repo . --out docs/refactor
	$(PYTHON) tools/list_skill_profiles.py --repo . --check
	$(PYTHON) tools/check_skill_mirror.py --repo .
	$(PYTHON) tools/check_prompt_assets.py --repo .
	$(PYTHON) tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all
	$(MAKE) test-fast
