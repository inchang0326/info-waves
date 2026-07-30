# Original Request

## 2026-07-29T22:12:12Z

You are Implementer 2 working on Milestone 2 (Popup Store Details) and Milestone 3 (Test Suite Hardening & 100% Pass) for Info Waves.
Your working directory is /Users/steady/.openclaw/workspace/info_waves/.agents/implementer_2.

Read the following design artifacts first:
- PROJECT.md: /Users/steady/.openclaw/workspace/info_waves/PROJECT.md
- ORIGINAL_REQUEST.md: /Users/steady/.openclaw/workspace/info_waves/.agents/ORIGINAL_REQUEST.md
- Explorer 2 Analysis: /Users/steady/.openclaw/workspace/info_waves/.agents/explorer_2/analysis.md
- Explorer 3 Analysis: /Users/steady/.openclaw/workspace/info_waves/.agents/explorer_3/analysis.md
- Challenger 1 Report: /Users/steady/.openclaw/workspace/info_waves/.agents/challenger_m1_1/challenge_report.md
- Reviewer 1 Report: /Users/steady/.openclaw/workspace/info_waves/.agents/reviewer_m1_1/review.md

Task instructions:
1. **Scraper Title Filter Refinement**: In `services/scraper_service.py`, refine `_fetch_realtime_brand_event()` title filtering to require the target `brand` name in RSS titles (or match brand context), preventing cross-brand title pollution (e.g. Starbucks promotion appearing for other brands).
2. **Milestone 2 (R2: Popup Store Details)**:
   - Enhance `services/location_service.py` to fetch dynamic detailed event info (operating hours, event status `🔥 진행중`, exhibition details, event schedule, news headlines) using Kakao Place Detail API (`https://place.map.kakao.com/main/v/{cid}`) and Live Search/RSS feeds when popup stores are searched.
   - Update `main.py` mapped popup item model to attach `description`, `event_status`, `schedule`, `event_content`, and `source_url`.
   - Update `services/ui_utils.py` (`generate_mini_popup_html` and `generate_card_html`) and `app.py` so map marker popups and list view cards render the detailed event description, status badges, operating hours, and event links.
3. **Milestone 3 (R3: Automated Tests & 100% Pytest Pass)**:
   - Add `pytest.ini` at project root `/Users/steady/.openclaw/workspace/info_waves/pytest.ini` with `[pytest]\ntestpaths = tests`.
   - Fix existing test failures across `tests/` (e.g. network rate-limit JSONDecodeError handling in location_service, mock side-effect isolation for keyword searches in test_main_pipeline/usecases, and marker color contract alignment in test_guzimap_integration).
   - Write new comprehensive test files under `/Users/steady/.openclaw/workspace/info_waves/tests`:
     - `tests/test_r1_dynamic_scraper.py`: Tests for R1 dynamic scraper and FallbackUrlManager link health check / 404 fallback.
     - `tests/test_r2_popup_details.py`: Tests for R2 popup store details fetching, model structure, map popup rendering, and list view cards.
     - `tests/test_r3_regression_prevention.py`: Regression prevention tests.
4. Run `pytest` across all test files and confirm a **100% pass rate** with 0 failures or errors.
5. Document all changes in /Users/steady/.openclaw/workspace/info_waves/.agents/implementer_2/changes.md and write a detailed handoff report with complete pytest logs in /Users/steady/.openclaw/workspace/info_waves/.agents/implementer_2/handoff.md.
