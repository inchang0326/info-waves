# Implementation Plan: GuziMap Address Landing URL Update

## Objective
Analyze GuziMap website (`https://xn--v69ak0xskm.com`) to determine the exact URL parameter structure for address pre-population and search, update `GuziMapScraper` in `services/scraper_service.py` to use this landing URL format instead of Naver Place fallback, update unit test assertions in `test_guzimap_integration.py`, and ensure all 85 pytest tests pass with zero regressions.

## Milestones & Execution Strategy

### Milestone 1: Exploration & GuziMap Parameter Analysis (R1)
- **Goal**: Find the exact URL parameter structure (e.g., `?q=`, `?search=`, path, hash, etc.) used by `https://xn--v69ak0xskm.com` for pre-filling and searching addresses.
- **Dispatch**:
  - `explorer_r1_1`: Investigate GuziMap web frontend using curl / HTTP requests / page inspection / JS bundle reverse engineering to find query parameter format for address search.
  - `explorer_r1_2`: Inspect current `services/scraper_service.py` (`GuziMapScraper`) implementation and how Naver Place redirection/fallback is currently built.
  - `explorer_r1_3`: Inspect `tests/test_guzimap_integration.py` and the entire 85-test suite to map out all assertions that need updating.
- **Deliverables**: Comprehensive handoff reports with confirmed URL structure and exact refactoring plan.

### Milestone 2: Implementation & Refactoring (R2)
- **Goal**: Update `GuziMapScraper` in `services/scraper_service.py` to return the GuziMap landing URL pre-populated with address parameters, removing Naver Place fallback. Update test assertions in `tests/test_guzimap_integration.py`.
- **Dispatch**:
  - `worker_r2_1`: Implement code changes in `services/scraper_service.py` and test updates in `tests/test_guzimap_integration.py`. Run pytest to verify all 85 tests pass.
- **Deliverables**: Modified code and passing build/pytest log report.

### Milestone 3: Verification & Integrity Audit (Acceptance Criteria)
- **Goal**: Conduct multi-agent verification:
  - 2 Reviewers (`reviewer_r2_1`, `reviewer_r2_2`): Code quality, interface compliance, edge case verification, URL encoding check.
  - 2 Challengers (`challenger_r2_1`, `challenger_r2_2`): Verification of landing URL format, testing address encoding (special characters, space encoding, Korean text), running test suite.
  - 1 Forensic Auditor (`auditor_r2_1`): Run integrity forensics checks to confirm clean implementation (no hardcoded test bypasses, genuine URL construction logic).
- **Deliverables**: Passing verification reports and CLEAN audit verdict.

## Verification Protocol
1. Pytest suite: 85/85 tests pass.
2. GuziMap URL format verified against `https://xn--v69ak0xskm.com` address search behavior.
3. Forensic Auditor verdict must be CLEAN.
