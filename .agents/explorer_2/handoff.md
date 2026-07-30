# Handoff Report — Explorer 2

## 1. Observation
- **Files Examined**:
  - `services/location_service.py` (lines 197–358, 360–410): Uses `_cached_search_nearby_brand` with Kakao Map search API (`https://search.map.kakao.com/mapsearch/map.daum`) to find nearby places based on brand queries. Returns list of dictionaries containing `name`, `address`, `road_address`, `lat`, `lon`.
  - `main.py` (lines 96–154): `fetch_local_alerts()` iterates over categories. For `"팝업스토어 & 전시/행사"`, it constructs mapped item dictionaries:
    ```python
    actual_title = f"[{p['name']}] {p.get('address', '')} - 실시간 팝업스토어 & 브랜드 행사진행 현황 (네이버 지도 실시간 상세보기)"
    actual_details = f"https://m.map.naver.com/search2/search.naver?query={query_encoded}"
    ```
    The data model contains no specific `description`, `event_status`, `schedule`, or `event_content` fields.
  - `app.py` (lines 870–898, 1003–1025): Invokes `generate_mini_popup_html()` for Leaflet/Folium map popups and `generate_card_html()` for the Streamlit list view expanders.
  - `services/ui_utils.py` (lines 303–404): `generate_card_html` and `generate_mini_popup_html` only accept `brand`, `title`, `link`, and optional `branches`. They render basic title and link without detailed event description, event status tags, or event schedules.
- **Verification Commands Executed**:
  - `pytest`: Passed 29/29 tests in 23.49s.
  - Kakao Place Detail API probe (`https://place.map.kakao.com/main/v/{cid}`): Verified returning structured operating hours (`openHour`), store category, tags, phone, homepage, and operation info.
  - Live news RSS probe (`https://news.google.com/rss/search?q={brand}+팝업스토어`): Verified returning real-time event headlines (e.g., `"데이지크, 성수동서 첫 대형 팝업스토어 오픈"`, `"동서식품 '카누 하우스' 누적 방문객 6만명 돌파"`) and direct article links.

## 2. Logic Chain
1. **Current Deficit**: When searching popup stores in a 3km radius (e.g., 성수동), 67 popup store locations are discovered via Kakao Map Search API. However, every popup item receives a static template string as its title (`[{brand}] {address} - 실시간 팝업스토어 & 브랜드 행사진행 현황...`) and lacks structured event fields (`description`, `event_status`, `schedule`, `event_content`).
2. **Impact on User Experience**: Map popups and list view cards only show generic place links rather than actual exhibition descriptions, operating hours, or event status.
3. **Data Source Feasibility**:
   - Kakao Map Search API returns `confirmid` (`cid`) for each popup place.
   - Calling `https://place.map.kakao.com/main/v/{cid}` yields operating hours (`openHour.periodList`), store contact, and tags.
   - Performing a lightweight live news RSS query (`https://news.google.com/rss/search?q={brand}+팝업스토어`) yields real news headlines, event topics, and direct press/event URLs.
4. **Data Model & UI Integration**:
   - Attaching `description`, `event_status`, `schedule`, `event_content`, and `source_url` to the popup store dictionary model allows `main.py` to pass rich metadata.
   - Enhancing `generate_mini_popup_html` and `generate_card_html` to check for these fields enables displaying status badges (`🔥 진행중`), event headlines/descriptions, operating hours (`⏰`), and event links on both map popups and list view cards.

## 3. Caveats
- Some temporary or newly registered popup store locations on Kakao Maps may not have Kakao Place detail records or news headlines. For these, a clean fallback mechanism (`✨ {popup_name} 브랜드 팝업스토어 및 체험형 브랜드 행사진행 현황`) is essential so no store displays empty or broken text.
- External HTTP detail requests should be executed with thread pool concurrency (`ThreadPoolExecutor`) and cached to avoid slowing down map search response times.

## 4. Conclusion
R2 (Popup Store Details on Map and List View) can be implemented effectively without breaking existing functionality or tests. By enhancing `services/location_service.py` to fetch dynamic event details (via Kakao Place Detail API + Live Web Search RSS), updating `main.py` to attach these fields to popup data models, and updating `services/ui_utils.py` / `app.py` to render them on map popups and list view cards, the application will fulfill requirement R2 with rich event descriptions. Detailed technical specifications are documented in `/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_2/analysis.md`.

## 5. Verification Method
1. **Analysis Verification**: Inspect `/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_2/analysis.md`.
2. **Current Test Baseline**: Run `pytest` from `/Users/steady/.openclaw/workspace/info_waves` to confirm all 29 tests pass.
3. **API Probe Verification**: Run:
   ```bash
   python -c "import requests; print(requests.get('https://place.map.kakao.com/main/v/1530932599').status_code)"
   ```
   Expect HTTP 200 with JSON payload containing `basicInfo` and `openHour`.
