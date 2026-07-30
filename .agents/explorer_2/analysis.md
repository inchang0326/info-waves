# Analysis: R2 - Popup Store Details on Map & List View

## Executive Summary
This document provides a comprehensive technical analysis, architectural diagnosis, and implementation design for **R2 (Popup Store Details on Map and List View)** in the Info Waves application.

Currently, when users search for popup stores in a location radius (e.g. 성수동, 홍대, 강남역), the application retrieves popup store locations via Kakao Map keyword search (`search_nearby_brand`), but formats each item title as a generic template string (`[{brand}] {address} - 실시간 팝업스토어 & 브랜드 행사진행 현황 (네이버 지도 실시간 상세보기)`). The popup store dictionary model lacks structured event detail fields (exhibition details, event status, schedule, event content, real headline/description), and both map marker popups and list view cards only render this generic title link.

To fulfill Requirement R2, we propose a concrete technical design that enriches popup store data model with real detailed event description fields, integrates real-time web scraping and Kakao Place Detail API lookup in `services/location_service.py` / `services/scraper_service.py`, and updates rendering functions in `services/ui_utils.py` and `app.py` to display these rich details on interactive map marker popups and detailed list view cards.

---

## 1. System Overview & Current Architecture

### 1.1 Data Flow of Popup Store Search
1. **User Request**: User searches a location (e.g., 성수동) or moves map and clicks "탐색" button.
2. **Global Alert Gathering (`fetch_global_alerts`)**:
   - `HybridOfficialScraper` returns base popup targets (e.g. "팝플리", "팝가", "더현대 팝업스토어", "신세계백화점 팝업스토어", "헤이팝" under category `"팝업스토어 & 전시/행사"`).
3. **Local Alert Mapping (`fetch_local_alerts` in `main.py`)**:
   - For category `"팝업스토어 & 전시/행사"`, `LocationService.search_nearby_brand()` executes query variants (`"{neighborhood} 팝업스토어"`, `"{short_dong} 팝업스토어"`, `"팝업스토어"`, `"팝업"`) against Kakao Map Search API (`https://search.map.kakao.com/mapsearch/map.daum`).
   - Deduplicates results by coordinate and place name (`coord_key`).
   - Builds mapped items for `"팝업스토어 & 전시/행사"`.
4. **Current Mapped Item Model (Before R2)**:
   ```python
   {
       "brand": "성수동공장 팝업스토어",
       "target": "성수동공장 팝업스토어",
       "title": "[성수동공장 팝업스토어] 서울 성동구 성수동2가 301-3 - 실시간 팝업스토어 & 브랜드 행사진행 현황 (네이버 지도 실시간 상세보기)",
       "details": "https://m.map.naver.com/search2/search.naver?query=...",
       "category": "팝업스토어 & 전시/행사",
       "orig_category": "팝업스토어 & 전시/행사",
       "address": "서울 성동구 성수동2가 301-3",
       "road_address": "서울 성동구 아차산로9길 10",
       "lat": 37.5441315,
       "lon": 127.0543621
   }
   ```
5. **UI Rendering (`app.py` & `services/ui_utils.py`)**:
   - **Map Marker Popup**: Generated via `generate_mini_popup_html(brand, title, link)`. Displays brand name, generic title string, and a "자세히 보기" link.
   - **List View Card**: Generated via `generate_card_html(brand, title, link, branch_items)`. Displays generic title and branch address, but lacks event description, schedule, or event status details.

---

## 2. Technical Gaps & Root Cause Analysis

| Component | Current State | Deficit / Gaps |
|---|---|---|
| **Data Model** | Standard location dict without event detail fields | Missing `description`, `event_status`, `schedule`, `event_content`, `source_url` |
| **Data Fetching** | Kakao Keyword Search API only returns basic place metadata (`name`, `address`, `lat`, `lon`, `confirmid`) | Detailed event description, exhibition content, operating schedule, and live event news are not dynamically queried |
| **Caching Layer** | `PersistentLocationCache` stores basic location array per neighborhood:brand | Cache structure only stores basic place list without event detail payload |
| **Map Marker Popup (`generate_mini_popup_html`)** | Renders brand logo, title, and external search URL | Does not render structured event description, status badge, operating hours, or event content |
| **List View Card (`generate_card_html`)** | Renders brand card with expandable branches | Does not render event description block, status tag, or schedule details |

---

## 3. Concrete Technical Design for R2

### 3.1 Data Model Extension
We extend the popup store dictionary object to include structured event details:

```python
mapped_item = {
    # Existing fields
    "brand": p["name"],
    "target": p["name"],
    "title": actual_title,
    "details": actual_details,
    "category": "팝업스토어 & 전시/행사",
    "orig_category": "팝업스토어 & 전시/행사",
    "address": p["address"],
    "road_address": p.get("road_address", ""),
    "lat": p.get("lat"),
    "lon": p.get("lon"),
    
    # NEW R2 Event Detail Fields:
    "description": event_details.get("description", ""),      # e.g., "📰 데이지크, 성수동서 첫 대형 팝업스토어 오픈" or "✨ 체험형 브랜드 팝업스토어"
    "event_status": event_details.get("event_status", "진행중"),  # e.g., "🔥 진행중", "⏰ 종료예정", "🎉 오픈"
    "schedule": event_details.get("schedule", ""),              # e.g., "매일 11:00 ~ 20:00"
    "event_content": event_details.get("event_content", ""),      # e.g., "전시, 체험존, 굿즈 증정"
    "source_url": event_details.get("source_url", "")          # e.g., Direct event news link or official page
}
```

### 3.2 Dynamic Event Description Fetching Architecture

We design a multi-tiered hybrid fetching service in `LocationService` (or `scraper_service` helper):

```
                       [Popup Store Searched]
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  Check Memory/Disk    │
                     │  Event Detail Cache   │
                     └───────────┬───────────┘
                                 │ Cache Miss
                                 ▼
        ┌─────────────────────────────────────────────────┐
        │       Parallel Multi-Source Detail Fetcher      │
        └────────┬───────────────────────┬────────────────┘
                 │                       │
                 ▼                       ▼
    ┌────────────────────────┐  ┌─────────────────────────┐
    │  Tier 1: Kakao Place   │  │ Tier 2: Real-time Web   │
    │  Detail API Lookup     │  │ Search (Google News RSS)│
    │  (place.map.kakao.com) │  │ & Brand Scrapers        │
    └───────────┬────────────┘  └────────────┬────────────┘
                │                            │
                │ Extract:                   │ Extract:
                │ - openHour (schedule)      │ - Live event news headline
                │ - tags / categories        │ - Official article/link
                │ - phone / operationInfo    │ - Event topic / theme
                └────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Reconcile & Synthesize Payload│
              │ - Format Description         │
              │ - Determine Event Status     │
              │ - Build Fallback if empty    │
              └──────────────┬───────────────┘
                             │
                             ▼
                 [Attach to Data Model]
```

#### Tier 1: Kakao Place Detail API Integration
- API Endpoint: `https://place.map.kakao.com/main/v/{confirmid}`
- HTTP Method: `GET` (User-Agent: `Mozilla/5.0`)
- Extracted Information:
  - `basicInfo.openHour.periodList[0].timeList`: Operating hours (e.g., "매일 11:00 ~ 20:00").
  - `basicInfo.tags`: Tag keywords (e.g., ["성수동팝업", "전시", "체험"]).
  - `basicInfo.phonenum`: Store contact.
  - `basicInfo.homepage`: Official website URL.

#### Tier 2: Real-Time Dynamic Web Search (Google News RSS / Scraper Integration)
- Query Format: `"{popup_name} 팝업스토어"` or `"{popup_name} 혜택 일정"`
- Endpoint: `https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko`
- Extracted Information:
  - Latest news article title within recent timeframe (e.g. "데이지크, 성수동서 첫 대형 팝업스토어 오픈").
  - Direct news article source URL (`source_url`).

#### Tier 3: Structured Fallback Synthesizer
- If Kakao Place Detail and Web Search yield minimal text, generate a clean structured fallback:
  - `description`: `"✨ {popup_name} 브랜드 팝업스토어 및 체험형 브랜드 행사진행 현황"`
  - `event_status`: `"🔥 진행중"`
  - `schedule`: `"영업시간 및 일정 매장 문의/상세보기 참조"`

### 3.3 UI Rendering Enhancements

#### 3.3.1 Interactive Map Marker Popup (`generate_mini_popup_html`)
Enhanced Popup Layout:
```html
<div style="font-family: 'Pretendard', sans-serif; min-width: 220px; padding: 6px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div style="display: flex; align-items: center;">
            <img src="{logo_url}" style="width: 24px; height: 24px; border-radius: 6px; margin-right: 8px;" />
            <strong style="font-size: 14px;">{brand}</strong>
        </div>
        <span style="background: #FEF3C7; color: #D97706; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 6px;">🔥 진행중</span>
    </div>
    <div style="font-size: 13px; font-weight: 600; color: #1F2937; margin-bottom: 6px;">
        {description}
    </div>
    <div style="font-size: 12px; color: #6B7280; margin-bottom: 8px;">
        📅 {schedule}
    </div>
    <div style="display: flex; gap: 8px;">
        <a href="{href}" target="_blank" style="font-size: 12px; color: #2563EB; font-weight: 700;">지도 상세보기</a>
        <a href="{source_url}" target="_blank" style="font-size: 12px; color: #059669; font-weight: 700;">행사 소식</a>
    </div>
</div>
```

#### 3.3.2 Detailed List View Card (`generate_card_html`)
Enhanced Card Layout:
- Renders an explicit **Event Description Box** (`.event-description-box`) below the card title:
  - **Status Tag**: `[🔥 진행중]` badge.
  - **Description Text**: Detailed event content / headline (`📰 데이지크, 성수동서 첫 대형 팝업스토어 오픈`).
  - **Schedule Info**: `⏰ Operating Hours / Schedule`.
  - **Content Keywords**: `🏷️ Tags / Exhibition details`.
  - **Direct Event Link**: Link to real event news / detail page.

---

## 4. Performance & Concurrency Considerations

1. **Parallel Execution**: Use `concurrent.futures.ThreadPoolExecutor` when fetching event details for multiple popup store candidates in `fetch_local_alerts()`.
2. **Caching Strategy**:
   - Extend `PersistentLocationCache` or add `_cached_fetch_popup_event_details(confirmid_or_name)` with LRU cache & SQLite storage.
   - Cache TTL or persistent disk storage ensures fast response times (< 1 second) on repeated explore requests.
3. **Graceful Fallbacks & Timeouts**: Set network timeout to 3-4 seconds per HTTP request to ensure map rendering never blocks or hangs.

---

## 5. Verification & Testing Strategy

1. **Unit Testing (`tests/test_location_service.py` & `tests/test_scraper_service.py`)**:
   - Verify `fetch_popup_event_details()` returns non-empty `description`, `event_status`, `schedule`.
   - Verify fallback mechanism when API / network fails.
2. **Integration Testing (`tests/test_requirements_verification.py` & `tests/test_usecases.py`)**:
   - Verify popup items returned by `fetch_local_alerts()` contain `description` key with rich text.
   - Run full test suite using `pytest` to guarantee 100% pass rate.
3. **UI Verification**:
   - Verify `generate_mini_popup_html` and `generate_card_html` render event description text cleanly without HTML breaking or escaping errors.

---

## 6. Implementation Roadmap (Recommended for Implementer)

| Step | Scope | Target File | Action |
|---|---|---|---|
| 1 | Service Layer | `services/location_service.py` | Implement `fetch_popup_event_details(brand, confirmid, address)` with Kakao Place Detail API + Google News RSS search & caching. |
| 2 | Main Pipeline | `main.py` | Integrate `fetch_popup_event_details()` into `fetch_local_alerts()` for category `"팝업스토어 & 전시/행사"`. Attach detailed event fields to mapped item dictionaries. |
| 3 | UI Utilities | `services/ui_utils.py` | Update `generate_mini_popup_html()` and `generate_card_html()` to display `description`, `event_status`, `schedule`, `event_content`, and event links. |
| 4 | Test Suite | `tests/test_requirements_verification.py` & `tests/test_location_service.py` | Write unit & integration tests verifying that popup stores returned by search contain real detailed event descriptions and pass `pytest`. |

