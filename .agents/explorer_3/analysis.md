# Detailed Analysis & Test Specification: Info Waves Enhancement (R3)

## Executive Summary
This document presents the detailed investigation, forensic audit, testing strategy, and test specifications for **R3 (Automated Tests & Regression Prevention)** of the Info Waves project. It complements the functional enhancements in **R1 (Dynamic Real-Time Scraper)** and **R2 (Popup Store Details Fetching & Display Model)**.

Our empirical audit of the existing test suite identified 10 failing tests out of 65 total tests across 13 test files in `tests/`, primarily caused by un-mocked external network dependencies (Kakao Maps API rate-limiting / HTML responses triggering `json.decoder.JSONDecodeError`), mocking overlap in `main.py` pipeline tests, UI marker color discrepancies, and root-level `pytest` collection errors in `scratch/`.

To guarantee a **100% pytest pass rate** across all existing and new test cases without regression, we provide a complete architecture for test infrastructure, mock setup, R1 & R2 test strategies, and exact test case specifications for 4 new test files under `tests/`.

---

## 1. Existing Test Suite Audit & Baseline Diagnosis

### 1.1 Directory Structure & Scope
The automated test suite is located in `/Users/steady/.openclaw/workspace/info_waves/tests/` and contains 14 files:
- `tests/__init__.py`
- `tests/test_scraper_service.py` (3 test cases)
- `tests/test_location_service.py` (10 test cases)
- `tests/test_app_execution.py` (2 test cases)
- `tests/test_main_pipeline.py` (3 test cases)
- `tests/test_guzimap_integration.py` (3 test cases)
- `tests/test_requirements_verification.py` (3 test cases)
- `tests/test_usecases.py` (21 test cases)
- `tests/test_performance_and_parity.py` (3 test cases)
- `tests/test_security_and_links.py` (4 test cases)
- `tests/test_stress.py` (3 test cases)
- `tests/test_ui_refinements.py` (3 test cases)
- `tests/test_ui_utils.py` (6 test cases)
- `tests/test_url_validity.py` (1 test case)

### 1.2 Baseline Execution Results
Execution of `./venv/bin/pytest tests` yielded:
- **Total Tests Collected**: 65 items
- **Passed**: 55 items (84.6%)
- **Failed**: 10 items (15.4%)

### 1.3 Detailed Root Cause Analysis of Existing Failures

| # | Failing Test File | Test Case Name | Root Cause | Fix Strategy |
|---|---|---|---|---|
| 1 | `test_guzimap_integration.py` | `test_guzimap_ui_styling_and_formatting` | Assertion error: expected `icon_info["color"] == "lightblue"`, but `ui_utils.py` returns `"black"`. | Synchronize marker color spec in `ui_utils.py` or test fixture to match UI design contract. |
| 2 | `test_location_service.py` | `test_gosanro_517_nearby_stores_detection` | External web endpoint `search.map.kakao.com` returned HTML block instead of JSON, triggering `JSONDecodeError` and empty list `[]`. | Provide fallback mock response for Kakao web search when network response fails or rate limits are hit. |
| 3 | `test_location_service.py` | `test_unlimited_store_collection_capacity` | Live network request blocked by rate limiter. | Mock multi-page Kakao search response with >25 stores. |
| 4 | `test_location_service.py` | `test_sanbon_gosanro_full_store_detection` | Live network request failed due to rate limiter / HTML response. | Add mock response fixture for brand searches. |
| 5 | `test_main_pipeline.py` | `test_fetch_local_alerts_mapping` | `LocationService.search_nearby_brand` mock returned `mock_places` for ALL queries, including keyword searches ("맛집", "가볼만한 곳"), causing `len(results) == 3` instead of expected `1`. | Use `side_effect` function on `search_nearby_brand` mock to return empty list `[]` for keyword searches. |
| 6 | `test_requirements_verification.py` | `test_requirement_3_taeseong_and_nationwide_store_richness` | Geocoding request for "태성로 107" failed due to live network blocking. | Mock geocoding search for "태성로 107" to return `(37.360, 126.920)`. |
| 7 | `test_security_and_links.py` | `test_search_place_taeseongro` | Live geocoding call failed due to Kakao web search rate limiting. | Mock search_place for "태성로 107". |
| 8 | `test_stress.py` | `test_st02_large_scale_local_mapping_thread_pool_stress` | Mocking overlap: `search_nearby_brand` returning mocked places for keyword searches added 2 extra items (102 vs expected 100). | Refine mock `side_effect` to isolate brand mapping from keyword searches. |
| 9 | `test_usecases.py` | `test_uc06_search_completion_lists_nearby_deals` | Same mocking overlap: keyword searches added 2 extra items (3 vs expected 1). | Refine mock `side_effect`. |
| 10 | `test_usecases.py` | `test_uc17_click_storm_same_location_consistency` | Same mocking overlap: keyword searches added 2 extra items (3 vs expected 1). | Refine mock `side_effect`. |

### 1.4 Root Collection Configuration Issue
Running `pytest` without specifying `tests` directory attempted to execute `scratch/test_fix_taeseong.py`, causing `1 error during collection` because scratch files contain unhandled top-level scripts.
**Solution**: Create `pyproject.toml` or `pytest.ini` with `testpaths = ["tests"]` and `norecursedirs = ["scratch", ".agents", "venv"]`.

---

## 2. Infrastructure & Mocking Architecture for Test Suite

### 2.1 Test Execution Harness & Fixtures
To decouple test execution from external networks (preventing HTTP 429/403 rate limits and timeout failures), we establish standard pytest fixtures:

```python
# Fixture for Session & Network Mocking
@pytest.fixture
def mock_kakao_places():
    return [
        {"name": "CU 산본역점", "address": "경기도 군포시 산본동 100", "road_address": "산본로 123", "lat": 37.361, "lon": 126.928},
        {"name": "GS25 산본점", "address": "경기도 군포시 산본동 200", "road_address": "번영로 456", "lat": 37.362, "lon": 126.929}
    ]

@pytest.fixture
def mock_location_service_smart(mock_kakao_places):
    def _search_side_effect(neighborhood, brand, lat_round=0.0, lon_round=0.0):
        # Keyword searches return empty to prevent item count pollution
        if brand in ["맛집", "가볼만한 곳"]:
            return ()
        return tuple(mock_kakao_places)
    return _search_side_effect
```

### 2.2 Pytest Configuration (`pyproject.toml` / `pytest.ini`)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
norecursedirs = scratch .agents venv data logs
```

---

## 3. Testing Strategy for R1 (Dynamic Real-Time Scraper)

### 3.1 Requirements Matrix for R1
- **R1-1: Dynamic Scraping Execution**: Replace hardcoded database list with dynamic web scraping (Playwright, BeautifulSoup, Open API, RSS).
- **R1-2: Data Contract Integrity**: Every returned item dictionary must contain `target` (brand), `title`, `details` (URL), `category`, `status`, and `event_description`.
- **R1-3: Fallback URL Handling**: If brand event URL returns HTTP 404, 500, timeout, or empty events, scraper MUST fall back to brand main page URL (e.g., `https://www.starbucks.co.kr`).

### 3.2 Dynamic Scraper Test Design

```
                     +----------------------------------+
                     | Dynamic Event Scraper Execution |
                     +----------------------------------+
                                      |
                     +----------------------------------+
                     |      HTTP / RSS / DOM Fetch      |
                     +----------------------------------+
                               /              \
                    Success   /                \ Error / 404 / 0 Events
                             v                  v
                 +-------------------+  +-----------------------+
                 | Parse Title, Link,|  | Graceful Fallback     |
                 | Description Text  |  | Main Page Brand URL   |
                 +-------------------+  +-----------------------+
                             \                  /
                              v                v
                     +----------------------------------+
                     | Validated Output Item Dictionary |
                     +----------------------------------+
```

---

## 4. Testing Strategy for R2 (Popup Store Details Fetching & Display Model)

### 4.1 Requirements Matrix for R2
- **R2-1: Popup Details Scraping**: When popups are found within radius, scrape actual event description (exhibit details, event status, operating hours).
- **R2-2: Marker Popup Integration**: `generate_mini_popup_html()` MUST render scraped popup details text alongside title, brand, address, and secure link (`target="_blank"`).
- **R2-3: Detailed List View Integration**: `generate_card_html()` MUST display detailed exhibition text, operating hours, and address copy button.

### 4.2 Popup Details Test Design

```
               +---------------------------------------+
               | Map Radius Search: Popup Category     |
               +---------------------------------------+
                                   |
               +---------------------------------------+
               | fetch_popup_store_details(popup, url) |
               +---------------------------------------+
                                   |
               +---------------------------------------+
               | Rich Event Description Text Extracted |
               +---------------------------------------+
                                  / \
                                 /   \
                                v     v
      +---------------------------+ +---------------------------+
      | Mini Popup Marker HTML    | | Detailed Card View List   |
      | (Title, Logo, Scraped Text| | (Expander, Full Summary,  |
      | & Secure Landing Link)    | | Address Copy Button)      |
      +---------------------------+ +---------------------------+
```

---

## 5. Specification of Exact New Test Cases under `tests/`

We outline 4 new test files to be implemented under `/Users/steady/.openclaw/workspace/info_waves/tests`:

### 5.1 `tests/test_r1_dynamic_scraper.py`

#### Test Case R1-01: `test_dynamic_scraper_output_contract()`
- **Objective**: Verify dynamic scraper returns valid list of dicts with all required contract keys (`target`, `title`, `details`, `category`).
- **Input**: Instantiation of dynamic scraper.
- **Assertion**:
  - `len(results) > 0`
  - For each item: `item["target"]` non-empty, `item["title"]` non-empty, `item["details"].startswith(("http://", "https://"))`, `item["category"]` valid.

#### Test Case R1-02: `test_starbucks_dynamic_event_parsing()`
- **Objective**: Verify dynamic parsing of Starbucks campaign list page HTML extracting event title and `pro_seq` view link.
- **Mock**: Mocks `sync_playwright` / HTML response with `.campaign_list dl dt a`.
- **Assertion**: Title matches mocked alt text, `details` URL contains `campaign_view.do?pro_seq=...`.

#### Test Case R1-03: `test_mcdonalds_dynamic_event_parsing()`
- **Objective**: Verify dynamic parsing of McDonald's promotion list HTML.
- **Mock**: Mocks `requests.get('https://www.mcdonalds.co.kr/kor/promotion/list.do')`.
- **Assertion**: Title parsed from `img alt`, details link formatted as `detail.do?promtNo=...`.

#### Test Case R1-04: `test_google_news_rss_dynamic_event_fetching()`
- **Objective**: Verify real-time Google News RSS event headline fetching for major brands.
- **Mock**: Mocks RSS XML containing `<item><title>스타벅스 100% 당첨 이벤트 - 연합뉴스</title></item>`.
- **Assertion**: Returned headline contains `& [신규] 스타벅스 100% 당첨 이벤트`.

#### Test Case R1-05: `test_fallback_url_on_404_not_found()`
- **Objective**: Verify fallback to main brand page URL when event page returns HTTP 404.
- **Mock**: `requests.get` returns `status_code = 404`.
- **Assertion**: Item `details` URL equals main landing page (e.g. `https://www.starbucks.co.kr`), `title` indicates fallback main page, no exception raised.

#### Test Case R1-06: `test_fallback_url_on_timeout_error()`
- **Objective**: Verify graceful fallback when event page times out.
- **Mock**: `requests.get` raises `requests.exceptions.Timeout`.
- **Assertion**: Returns valid item with main brand URL, scraper does not crash.

#### Test Case R1-07: `test_fallback_url_on_empty_events()`
- **Objective**: Verify fallback when event DOM selector returns 0 event items.
- **Mock**: Mocks valid HTML page without event cards.
- **Assertion**: Falls back to main brand page URL with default fallback banner.

#### Test Case R1-08: `test_concurrent_dynamic_scraping_thread_safety()`
- **Objective**: Verify thread-safe concurrent execution of multiple dynamic scrapers via `ThreadPoolExecutor`.
- **Assertion**: All scrapers complete within 3.0s without race conditions.

---

### 5.2 `tests/test_r2_popup_details.py`

#### Test Case R2-01: `test_popup_detail_scraper_extraction()`
- **Objective**: Verify detailed text scraping for popups (exhibit info, operating dates, event status).
- **Mock**: Mocks Naver Place / heyPOP detail HTML containing `<div class="popup_desc">...</div>`.
- **Assertion**: Returned dict contains `popup_details` / `description` field with full scraped text.

#### Test Case R2-02: `test_popup_detail_fallback_on_scraping_error()`
- **Objective**: Verify fallback description when popup detail page fails to load.
- **Assertion**: Returns structured fallback string: `[더현대 서울] 실시간 팝업스토어 & 행사 진행 현황 (상세보기 클릭)`.

#### Test Case R2-03: `test_fetch_local_alerts_includes_popup_details()`
- **Objective**: Verify `fetch_local_alerts()` populates popup category items with detailed text.
- **Assertion**: Items under `"팝업스토어 & 전시/행사"` contain `popup_details` / rich description text.

#### Test Case R2-04: `test_generate_mini_popup_html_with_details()`
- **Objective**: Verify Folium marker popup HTML includes scraped detailed popup description text.
- **Assertion**: `generate_mini_popup_html` output contains detailed event text, brand, address, and `target="_blank"`.

#### Test Case R2-05: `test_generate_card_html_with_popup_details()`
- **Objective**: Verify card view HTML renders popup description, operating hours, and address copy button.
- **Assertion**: `generate_card_html` output contains popup description section and `copy-addr-btn`.

---

### 5.3 `tests/test_r3_regression_prevention.py`

#### Test Case R3-01: `test_all_16_categories_schema_integrity()`
- **Objective**: Verify `categorized_results` dictionary contains all 16 predefined categories.
- **Assertion**: All categories present, list values, schema backward compatibility maintained.

#### Test Case R3-02: `test_cache_integrity_with_dynamic_results()`
- **Objective**: Verify SQLite WAL and LRU cache store and retrieve dynamic event data without corruption.
- **Assertion**: Cached items match original dynamic results with 100% field parity.

#### Test Case R3-03: `test_main_pipeline_error_isolation()`
- **Objective**: Verify single scraper exception in `_run_scrapers()` is caught and logged, allowing other scrapers to finish.
- **Assertion**: Pipeline returns results from working scrapers without throwing exception.

#### Test Case R3-04: `test_full_suite_100_percent_pass_guarantee()`
- **Objective**: Comprehensive suite sanity check verifying zero failures across all test files.

---

### 5.4 Root Pytest Configuration Fix

Add `/Users/steady/.openclaw/workspace/info_waves/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
norecursedirs = scratch .agents venv data logs
```

---

## 6. Regression Prevention & Verification Plan

### 6.1 Independent Verification Command
```bash
./venv/bin/pytest tests -o cache_dir=/tmp/pytest_cache_tmp
```

### 6.2 Verification Criteria
1. **Pass Rate**: 100% (0 failures, 0 errors).
2. **Execution Time**: Entire test suite finishes in under 35 seconds.
3. **Network Isolation**: All external API calls mocked or fallback-handled during automated test execution.
4. **Layout Compliance**: All test files co-located inside `/Users/steady/.openclaw/workspace/info_waves/tests/`. No test code inside `.agents/`.

---

## Conclusion
This specification provides an exhaustive, airtight blueprint for **R3 (Automated Tests & Regression Prevention)**. By fixing existing mock overlaps and network dependencies while adding comprehensive test cases for **R1 (Dynamic Scraper)** and **R2 (Popup Details)**, the Info Waves project will maintain a 100% pytest pass rate.
