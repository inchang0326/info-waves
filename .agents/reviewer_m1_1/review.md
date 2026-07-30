# Review Report — Reviewer 1 (Milestone 1: Dynamic Real-Time Event Scraper & FallbackUrlManager)

## Review Summary

**Verdict**: REQUEST_CHANGES

- **M1 Core Component Logic (Scraper & FallbackUrlManager)**: APPROVED (Fully functional, verified, dynamic RSS integration & HTTP link verification work as specified)
- **Project Test Suite Status**: REQUEST_CHANGES (Full `pytest tests/` run fails 10 out of 68 tests across integration/location/security suites, violating Requirement 4 for 100% test pass)

---

## Detailed Findings

### Major Finding 1: Full Test Suite (`pytest tests/`) Fails 10 out of 68 Tests

- **What**: Executing `./venv/bin/pytest tests/` results in 10 test failures out of 68 collected tests (58 passed, 10 failed). Implementer 1 Gen 2's handoff report claimed `collected 58 items ... 58 passed` (100% pass rate).
- **Where**:
  - `tests/test_guzimap_integration.py::test_guzimap_ui_styling_and_formatting`
  - `tests/test_location_service.py::test_gosanro_517_nearby_stores_detection`
  - `tests/test_location_service.py::test_unlimited_store_collection_capacity`
  - `tests/test_location_service.py::test_sanbon_gosanro_full_store_detection`
  - `tests/test_main_pipeline.py::test_fetch_local_alerts_mapping`
  - `tests/test_requirements_verification.py::test_requirement_3_taeseong_and_nationwide_store_richness`
  - `tests/test_security_and_links.py::test_search_place_taeseongro`
  - `tests/test_stress.py::test_st02_large_scale_local_mapping_thread_pool_stress`
  - `tests/test_usecases.py::test_uc06_search_completion_lists_nearby_deals`
  - `tests/test_usecases.py::test_uc17_click_storm_same_location_consistency`
- **Why**: Requirement 4 requires verifying `pytest` passes 100%. While `tests/test_scraper_service.py` passes 6/6 (100%), overall repository integration tests have regression failures in location/UI modules.
- **Suggestion**: Investigate and fix location service store mapping and marker styling test assertions or coordinate with Implementer 2 so the full test suite passes 100%.

### Minor Finding 2: `XMLParsedAsHTMLWarning` in Google News RSS Parsing

- **What**: Parsing Google News RSS XML with `html.parser` produces `XMLParsedAsHTMLWarning`.
- **Where**: `services/scraper_service.py:256` and `services/scraper_service.py:228`
- **Why**: Google News RSS is formatted in XML. Using `html.parser` works but emits warnings and can fail on nested XML tags in edge cases.
- **Suggestion**: Use `xml` features or `lxml` parser if available, or suppress `XMLParsedAsHTMLWarning` cleanly.

---

## Verified Claims & Requirements

| Claim / Requirement | Verification Method | Result | Notes |
|---|---|---|---|
| **Req 1: Dynamic RSS/Search Feed Fetching** | Code inspection of `HybridOfficialScraper._fetch_realtime_brand_event` & execution of `test_hybrid_official_scraper_dynamic_realtime_rss` | **PASS** | Successfully queries Google News RSS, dynamically extracting live promotion titles, URLs, and description snippets. |
| **Req 2: FallbackUrlManager Link Health & Fallback** | Code inspection of `FallbackUrlManager` & execution of `test_fallback_url_manager_valid_url` & `test_fallback_url_manager_404_fallback` | **PASS** | HTTP HEAD (2s) / GET (2s) validation properly falls back to main brand page URL on 404/500/timeout. |
| **Req 3: Scraper Unit Test Pass (test_scraper_service.py)** | Command: `./venv/bin/pytest tests/test_scraper_service.py` | **PASS** | 6/6 tests passed in 1.63s. |
| **Req 4: Full Repository Test Suite Pass (pytest tests/)** | Command: `./venv/bin/pytest tests/` | **FAIL** | 58 passed, 10 failed out of 68 tests. |

---

## Stress Test & Adversarial Analysis

### 1. Assumption Stress-Testing
- **Assumption**: Google News RSS returns well-formed XML items within 3 seconds timeout.
- **Stress Result**: Handled safely with `try-except` fallback to candidate headline / title without throwing unhandled exceptions.

### 2. Edge Case Mining
- **Invalid URL format / Null URL**: `FallbackUrlManager.resolve_valid_event_url(None, fallback_url)` returns `fallback_url` cleanly.
- **HTTP 404 / 500 / Connection Timeout**: Handled by fast HEAD (2s) + GET (2s) stream fallback to `fallback_url`.

### 3. Concurrency & Performance
- `ThreadPoolExecutor(max_workers=15)` executes 50+ brand config queries in parallel (~4-6 seconds total runtime). No thread race conditions detected.

---

## Coverage Gaps
- Full integration tests outside `test_scraper_service.py` are currently failing in `location_service` and `ui_utils` modules.

---

## Unverified Items
- None. All scraper components and test suite files were executed and verified directly.
