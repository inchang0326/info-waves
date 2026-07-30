# Handoff Report — Explorer R1-3 (Milestone 1 Test Suite Analysis)

## 1. Observation

### Test Suite Overview & Total Test Count
A total of **85 tests** were identified across **16 test files** in `/Users/steady/.openclaw/workspace/info_waves/tests`.

| # | Test File | Test Count | Test Functions |
|---|---|---|---|
| 1 | `tests/test_app_execution.py` | 2 | `test_app_compilation_integrity`, `test_app_script_execution_and_rendering` |
| 2 | `tests/test_guzimap_integration.py` | 3 | `test_guzimap_scraper_data_fetching`, `test_guzimap_local_alert_geofencing`, `test_guzimap_ui_styling_and_formatting` |
| 3 | `tests/test_location_service.py` | 10 | `test_haversine_distance_calculation`, `test_get_neighborhood_fallback_on_exception`, `test_search_nearby_brand_filtering`, `test_search_nearby_brand_distance_filtering`, `test_get_current_location_ip_and_fallback`, `test_search_place_coordinates`, `test_gosanro_517_nearby_stores_detection`, `test_unlimited_store_collection_capacity`, `test_popup_store_strict_geofencing`, `test_sanbon_gosanro_full_store_detection` |
| 4 | `tests/test_main_pipeline.py` | 3 | `test_run_scrapers_categorization`, `test_fetch_global_alerts`, `test_fetch_local_alerts_mapping` |
| 5 | `tests/test_performance_and_parity.py` | 3 | `test_10_coordinates_data_parity_and_2tier_cache_integrity`, `test_sqlite_wal_persistence_across_cache_flushes`, `test_local_deals_guzimap_and_list_parity_and_exposure` |
| 6 | `tests/test_r1_dynamic_scraper.py` | 8 | `test_dynamic_scraper_output_contract`, `test_cross_brand_title_pollution_prevention`, `test_brand_matches_title_helper`, `test_mcdonalds_dynamic_event_parsing`, `test_fallback_url_on_404_not_found`, `test_fallback_url_on_timeout_error`, `test_fallback_url_on_invalid_scheme`, `test_concurrent_dynamic_scraping_thread_safety` |
| 7 | `tests/test_r2_popup_details.py` | 5 | `test_fetch_popup_event_details_structure`, `test_fetch_local_alerts_attaches_popup_details`, `test_generate_mini_popup_html_with_details`, `test_generate_card_html_with_popup_details`, `test_popup_detail_fallback_on_network_error` |
| 8 | `tests/test_r3_regression_prevention.py` | 4 | `test_all_16_categories_schema_integrity`, `test_main_pipeline_error_isolation`, `test_cache_integrity_with_dynamic_results`, `test_category_marker_icon_fallback_safety` |
| 9 | `tests/test_requirements_verification.py` | 3 | `test_requirement_1_brand_logos_not_universe_fallback`, `test_requirement_2_location_search_component_trigger_logic`, `test_requirement_3_taeseong_and_nationwide_store_richness` |
| 10 | `tests/test_scraper_service.py` | 6 | `test_abstract_scraper_raises_not_implemented`, `test_ruliweb_hotdeal_scraper_structure`, `test_hybrid_official_scraper_base_data_integrity`, `test_fallback_url_manager_valid_url`, `test_fallback_url_manager_404_fallback`, `test_hybrid_official_scraper_dynamic_realtime_rss` |
| 11 | `tests/test_security_and_links.py` | 4 | `test_gitignore_security`, `test_card_links_target_blank_and_escaping`, `test_popup_links_target_blank_and_escaping`, `test_search_place_taeseongro` |
| 12 | `tests/test_stress.py` | 3 | `test_st01_scraper_concurrency_and_performance_benchmark`, `test_st02_large_scale_local_mapping_thread_pool_stress`, `test_st03_lru_cache_high_concurrency_stress` |
| 13 | `tests/test_ui_refinements.py` | 3 | `test_brand_logo_uses_official_domain_s2_favicons`, `test_ui_css_rules_restored_to_stable_layout`, `test_targeted_spinner_active_only_on_app_load_and_search_button` |
| 14 | `tests/test_ui_utils.py` | 6 | `test_get_brand_logo`, `test_get_zoom_for_radius`, `test_generate_card_html_single`, `test_generate_card_html_with_branches`, `test_generate_mini_popup_html`, `test_format_expander_title` |
| 15 | `tests/test_url_validity.py` | 1 | `test_all_brand_urls_non_404` |
| 16 | `tests/test_usecases.py` | 21 | `test_uc01_location_search_centers_map_and_resets_list` through `test_uc21_location_key_auto_synchronization_and_guzimap_guaranteed_recommendation` |
| **Total** | **16 Files** | **85** | Target: 85 tests (100% matched) |

---

### Detailed Inspection of `tests/test_guzimap_integration.py`

File Path: `/Users/steady/.openclaw/workspace/info_waves/tests/test_guzimap_integration.py`

Verbatim Content of `test_guzimap_scraper_data_fetching`:
```python
7: def test_guzimap_scraper_data_fetching():
8:     """거지맵(GuziMap) API에서 초저가/가성비 식당 데이터를 정확히 수집하는지 검증합니다."""
9:     fake_guzi_data = [
10:         {
11:             "id": "test-id-1",
12:             "name": "짜신 산본본점",
13:             "address": "경기도 군포시 광정로 68",
14:             "latest_menu_name": "짜장면",
15:             "latest_price_krw": 3000,
16:             "lat": 37.3602,
17:             "lng": 126.9204,
18:             "naver_place_id": "12345678"
19:         }
20:     ]
21:     
22:     with patch("requests.get") as mock_get:
23:         mock_resp = MagicMock()
24:         mock_resp.status_code = 200
25:         mock_resp.json.return_value = fake_guzi_data
26:         mock_get.return_value = mock_resp
27:         
28:         scraper = GuziMapScraper()
29:         results = scraper.scrape()
30:         
31:         assert len(results) == 1
32:         item = results[0]
33:         assert item["category"] == "거지맵 (가성비 식당 & 초저가 혜택)"
34:         assert "짜신 산본본점" in item["target"]
35:         assert "3,000원" in item["title"]
36:         assert "https://xn--v69ak0xskm.com/?q=" in item["details"]
37:         assert "%EA%B2%BD%EA%B8%B0%EB%8F%84" in item["details"]
38:         assert item["lat"] == 37.3602
39:         assert item["lon"] == 126.9204
```

#### Observations in `test_guzimap_integration.py`:
1. **`test_guzimap_scraper_data_fetching` (lines 7–40)**:
   - Line 36 explicitly asserts `assert "https://xn--v69ak0xskm.com/?q=" in item["details"]`.
   - Line 37 explicitly asserts `assert "%EA%B2%BD%EA%B8%B0%EB%8F%84" in item["details"]` (URL-encoded address `urllib.parse.quote("경기도 군포시 광정로 68")`).
   - Line 18 in mock data contains `"naver_place_id": "12345678"`, but `GuziMapScraper` ignores Naver Place IDs and generates `https://xn--v69ak0xskm.com/?q={encoded_address}`.
2. **`test_guzimap_local_alert_geofencing` (lines 41–72)**:
   - Line 46 uses `"details": "https://xn--v69ak0xskm.com"` as fixture data.
   - Line 55 uses `"details": "https://xn--v69ak0xskm.com"` as fixture data.
3. **`test_guzimap_ui_styling_and_formatting` (lines 73–88)**:
   - Verifies expander title formatting (`"거지맵 (가성비 식당) (5개)"`), marker icon (`color: black`, `icon: cutlery`), and category inference (`infer_category_from_brand`).

---

### Related URL & Details Assertions Across Other Test Files

1. **`tests/test_url_validity.py`**:
   - Lines 41–42:
     ```python
     naver_search_urls = [item.get("details") for item in items if "search.naver.com" in item.get("details", "")]
     assert len(naver_search_urls) == 0, f"Found Naver search landing URLs: {naver_search_urls}"
     ```
   - **Key Finding**: Explicitly asserts that NO scraper item outputs Naver search URLs (`search.naver.com`). GuziMap search landing URLs (`https://xn--v69ak0xskm.com/?q=...`) comply with this constraint.

2. **`tests/test_performance_and_parity.py`**:
   - Line 100 & 129:
     ```python
     "details": "https://naver.me/guzi_test"
     assert guzi_category_list[0]["details"] == "https://naver.me/guzi_test"
     ```
   - Uses mock placeholder `https://naver.me/guzi_test` in fixture data to verify parity in `fetch_local_alerts`.

3. **`tests/test_usecases.py`**:
   - Line 343:
     ```python
     "details": "https://naver.me/test"
     ```
   - Uses mock placeholder in fixture data for `test_uc21_location_key_auto_synchronization_and_guzimap_guaranteed_recommendation`.

---

## 2. Logic Chain

1. **Observation**: `GuziMapScraper` in `services/scraper_service.py` currently builds item details links via `link = f"https://xn--v69ak0xskm.com/?q={encoded_addr}"` (where `xn--v69ak0xskm.com` is Punycode for `거지맵.com`).
2. **Observation**: `test_guzimap_scraper_data_fetching` (lines 36–37) directly checks for `"https://xn--v69ak0xskm.com/?q="` and URL-encoded address strings (`"%EA%B2%BD%EA%B8%B0%EB%8F%84"`).
3. **Logic**: When `GuziMapScraper` is updated/refactored to return GuziMap address search landing URLs, the primary verification point is in `test_guzimap_scraper_data_fetching`.
4. **Logic**: If the URL format in `GuziMapScraper` is changed (e.g. parameter name, UTF-8 vs Punycode domain, or path structure), assertions on lines 36–37 in `tests/test_guzimap_integration.py` will fail unless updated to match the new URL pattern.
5. **Logic**: `test_url_validity.py` (lines 41–42) verifies that no URLs fall back to Naver search (`search.naver.com`). GuziMap landing URLs (`https://xn--v69ak0xskm.com/?q=...`) pass this validation.

---

## 3. Caveats

1. **Read-Only Mode**: This investigation was strictly read-only. No source files or test files outside the agent directory were modified.
2. **Punycode vs Unicode Domain**: `xn--v69ak0xskm.com` is the Punycode representation of `거지맵.com`. Depending on whether `urllib.parse` or browsers normalize the domain, tests checking for `"xn--v69ak0xskm.com"` vs `"거지맵.com"` must maintain string format consistency.
3. **Mock Data Placeholders**: `test_performance_and_parity.py` and `test_usecases.py` use static mock URL strings (`https://naver.me/guzi_test`). These test `fetch_local_alerts` parameter pass-through rather than `GuziMapScraper` logic, so they do not require modification unless mock fixture standards are updated.

---

## 4. Conclusion

- **Total Test Count**: 85 tests across 16 files (100% matched with target).
- **Primary Update Requirement**: `tests/test_guzimap_integration.py` -> `test_guzimap_scraper_data_fetching()` (lines 36–37).
- **Secondary Alignment Requirements**:
  - `tests/test_guzimap_integration.py` -> `test_guzimap_local_alert_geofencing()` fixture details (lines 46, 55).
  - `tests/test_url_validity.py` -> `test_all_brand_urls_non_404()` (lines 41–42) ensures no Naver search links are generated.

---

## 5. Verification Method

### Test Count & Baseline Status Commands:
```bash
# 1. Verify test count (Target: 85 tests)
python3 -m pytest --co -q

# 2. Run GuziMap integration tests
python3 -m pytest tests/test_guzimap_integration.py -v

# 3. Run full test suite
python3 -m pytest -v
```
