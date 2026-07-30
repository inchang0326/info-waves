# Challenge Report — Milestone 1 (Dynamic Real-Time Event Scraper & FallbackUrlManager)

## Challenge Summary

**Overall risk assessment**: HIGH

The implementation of `FallbackUrlManager` and `HybridOfficialScraper` in `services/scraper_service.py` successfully delivers real-time event fetching via parallel Google News RSS queries and link fallback resolution. Basic unit tests in `test_scraper_service.py` pass 6/6.

However, empirical stress-testing surfaced a **HIGH severity cross-brand headline pollution flaw** in `HybridOfficialScraper._fetch_realtime_brand_event()`, where generic keyword matching causes news headlines belonging to unrelated brands (e.g. Starbucks) to be attached to target brands (e.g. 천년닭강정). Furthermore, executing `pytest` across the full test suite (`tests/`) revealed **10 test failures out of 68 collected items**, caused by Kakao API response parsing errors in `location_service.py` (`JSONDecodeError`) and marker color assertion mismatches in UI tests.

---

## Challenges

### [High Risk] Challenge 1: Cross-Brand Keyword Pollution in `_fetch_realtime_brand_event()`

- **Assumption challenged**: That checking `any(kw in raw_title for kw in [brand, "이벤트", "할인", "프로모션", "세일", "팝업", "혜택"])` ensures the RSS title is relevant to the target `brand`.
- **Attack scenario**:
  Google News RSS query for a niche target brand (e.g. `천년닭강정`) may return an RSS feed containing an article about a major brand discount, e.g. `"스타벅스, 서머 음료 50% 할인 이벤트 진행"`. Because `"할인"` is present in the generic keyword list, `_fetch_realtime_brand_event()` evaluates the match to `True` and assigns `[실시간 혜택] 스타벅스, 서머 음료 50% 할인 이벤트 진행` to target `"천년닭강정"`.
- **Blast radius**:
  Misleading brand information displayed to end users in UI / API, where Brand A displays promotional headlines from Brand B.
- **Empirical Proof**:
  Verified via `test_rss_matching_flaw.py`. Mocking RSS return with Starbucks discount for target `천년닭강정` produced:
  `Target: 천년닭강정 | Title: [실시간 혜택] 스타벅스, 서머 음료 50% 할인 이벤트 진행` (Polluted: `True`).
- **Suggested Mitigation**:
  Require that the target `brand` (or an explicit alias/keyword specific to that brand) MUST be present in the title/description, OR remove generic single words (`"할인"`, `"이벤트"`) from the title acceptance filter.

---

### [High Risk] Challenge 2: Test Suite Integration Failures (10/68 Failed)

- **Assumption challenged**: Implementer claimed 100% pytest pass rate (58/58 passed).
- **Attack scenario**:
  Running `venv/bin/pytest tests/` executes 68 test items across 14 test files. 10 tests failed:
  1. `test_guzimap_ui_styling_and_formatting`: AssertionError (`'black' == 'lightblue'`).
  2. `test_gosanro_517_nearby_stores_detection`: Unhandled `JSONDecodeError` in `location_service.py:281` (`data = json.loads(text)`).
  3. `test_unlimited_store_collection_capacity`: `assert 0 > 25` due to Kakao Maps JSON decode failure.
  4. `test_sanbon_gosanro_full_store_detection`: Kakao Maps API response failure.
  5. `test_fetch_local_alerts_mapping`: Failed assertion.
  6. `test_requirement_3_taeseong_and_nationwide_store_richness`: Failed assertion.
  7. `test_search_place_taeseongro`: Failed assertion.
  8. `test_st02_large_scale_local_mapping_thread_pool_stress`: Thread pool location search failure.
  9. `test_uc06_search_completion_lists_nearby_deals`: Search completion empty array.
  10. `test_uc17_click_storm_same_location_consistency`: Consistency assertion failure.
- **Blast radius**:
  Location service features fail silently or return 0 stores when API key or response format fluctuates, breaking search and map features.
- **Suggested Mitigation**:
  Add defensive error handling and fallbacks in `location_service.py` around `json.loads(text)`, and fix marker color assertions.

---

### [Medium Risk] Challenge 3: FallbackUrlManager Behavior on Invalid / None Fallback URLs

- **Assumption challenged**: That `fallback_url` passed into `FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)` is always a valid, non-null HTTP URL.
- **Attack scenario**:
  If `event_url` is broken/404 and `fallback_url` is `None` or an empty string `""`, `resolve_valid_event_url` returns `None` or `""` without attempting default validation or falling back to a safe system default landing page.
- **Blast radius**:
  Scraped event dict containing `details: None` or `details: ""` which can break UI link rendering or downstream parsers.
- **Suggested Mitigation**:
  Implement a global default fallback URL (e.g. `"https://xn--v69ak0xskm.com"` or base brand website) when `fallback_url` is empty or invalid.

---

### [Medium Risk] Challenge 4: Pytest Collection Failure at Workspace Root (`scratch/test_fix_taeseong.py`)

- **Assumption challenged**: That `pytest` passes clean collection across the workspace.
- **Attack scenario**:
  Executing `pytest` from root directory (`/Users/steady/.openclaw/workspace/info_waves`) attempts to collect all `test_*.py` files, including `scratch/test_fix_taeseong.py`, which crashes with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` during module import.
- **Blast radius**:
  CI/CD test runners or standard `pytest` invocation fails immediately at collection phase unless restricted to `tests/`.
- **Suggested Mitigation**:
  Exclude `scratch/` from pytest root collection via `pytest.ini` (`norecursedirs = scratch .agents`).

---

### [Low Risk] Challenge 5: XMLParsedAsHTMLWarning & Deprecation Escape Warnings

- **Assumption challenged**: BeautifulSoup HTML parser handles Google News RSS XML cleanly without warnings.
- **Attack scenario**:
  `BeautifulSoup(resp.text, 'html.parser')` on RSS XML produces `XMLParsedAsHTMLWarning` across logs. In addition, regex string on line 135 in `scraper_service.py` contains invalid escape sequence `\(`.
- **Blast radius**:
  Log noise and potential parsing inaccuracies on malformed XML.
- **Suggested Mitigation**:
  Use `features="xml"` (if `lxml` is available) or suppress warning cleanly; fix raw string for regex `r"goView\('(\d+)'\)"`.

---

## Stress Test Results

| Scenario | Target | Expected Behavior | Actual Behavior | Pass/Fail |
|---|---|---|---|---|
| HTTP 404 Event URL | FallbackUrlManager | Fallback to `fallback_url` | Returned `fallback_url` | PASS |
| HTTP 500 Event URL | FallbackUrlManager | Fallback to `fallback_url` | Returned `fallback_url` | PASS |
| HTTP 403/502/503/504 URLs | FallbackUrlManager | Fallback to `fallback_url` | Returned `fallback_url` | PASS |
| Invalid URL Schemes (`ftp://`, `javascript:`, `None`) | FallbackUrlManager | Fallback to `fallback_url` | Returned `fallback_url` | PASS |
| Connection Timeout / Network Error | FallbackUrlManager | Fallback to `fallback_url` within 4s | Returned `fallback_url` in 2-4s | PASS |
| Single Scrape Data Field Integrity | HybridOfficialScraper | 40+ items with non-empty fields & valid URLs | Scraped 107 items; all fields valid | PASS |
| Concurrency Stress Test | HybridOfficialScraper | 3 parallel `scrape()` calls complete < 45s | Completed in 4.46s (107 items each) | PASS |
| RSS Keyword Matching Relevance | HybridOfficialScraper | RSS titles must match target brand | Generic keywords cause cross-brand title pollution | **FAIL** |
| Root `pytest` Execution | Test Suite | 100% pass across workspace | Collection error in `scratch/test_fix_taeseong.py` | **FAIL** |
| Full `pytest tests/` Execution | Test Suite | 100% pass across `tests/` | 10 failed, 58 passed in 21.44s | **FAIL** |

---

## Unchallenged Areas

- **Playwright live rendering performance for Starbucks dynamic crawler**: Playwright headless execution depends on local browser installation and system GUI resources; not tested under extreme OS memory starvation.
