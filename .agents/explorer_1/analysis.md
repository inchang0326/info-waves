# Technical Analysis & Dynamic Real-Time Scraper Design (R1)

## Executive Summary
This document details the forensic investigation of the existing event scraping mechanism in **Info Waves** (`services/scraper_service.py`) and presents a concrete technical architecture for **R1: Dynamic Real-Time Event Scraper**.

Currently, event information is heavily reliant on static hardcoded titles and landing URLs defined inside `HybridOfficialScraper.base_data`. The goal of R1 is to replace hardcoded data with dynamic, real-time fetching (combining RSS feeds, HTML web scraping, and search/open APIs) while guaranteeing graceful fallback to main brand page URLs whenever an event page fails or is missing.

---

## 1. Current Codebase Investigation

### 1.1 `services/scraper_service.py` Analysis
- **Location**: `/Users/steady/.openclaw/workspace/info_waves/services/scraper_service.py` (lines 178–351)
- **Primary Scraper**: `HybridOfficialScraper`
- **Data Structure**:
  - `scrape()` returns a list of dictionaries with required fields: `target`, `title`, `details`, `category`.
  - `base_data` contains over 50 hardcoded brand entries. Example:
    ```python
    {"target": "CU", "title": "쓔퍼세일 & 이달의 1+1/2+1 득템 혜택", "details": "https://cu.bgfretail.com/event/plus.do?category=event", "category": "편의점 혜택"},
    {"target": "버거킹", "title": "와퍼주니어 반값 & 올데이킹(ALL DAY KING) 혜택", "details": "https://www.burgerking.co.kr/#/event", "category": "외식/패스트푸드 및 피자/치킨"},
    ```
- **Current Dynamic Component**:
  - `_fetch_news_headline(brand)`: Queries Google News RSS (`https://news.google.com/rss/search?q={brand}+이벤트+when:30d&hl=ko&gl=KR&ceid=KR:ko`).
  - If a headline is found, it appends `f" & [신규] {title}"` to the **hardcoded base title**.
  - If RSS fails or yields no results, it falls back **100% to the hardcoded static string**.

### 1.2 Identified Deficiencies
1. **Hardcoded Base Data**: Event titles (e.g. "와퍼주니어 반값", "올영세일") do not update dynamically when brand promotions change.
2. **Missing Granular Event Details**: No direct extraction of specific event start/end dates, event descriptions, or event-specific landing pages.
3. **Fragile Link Handling**: If a specific event page link breaks or is discontinued, there is no dynamic health check or explicit fallback mechanism to default safely to the main brand page.

---

## 2. External Dependencies Assessment

### 2.1 Available Environment Packages
Inspected `requirements.txt` and python environment (`pip list`):
- `requests==2.31.0` / `requests==2.32.3`: Synchronous HTTP client with session support.
- `beautifulsoup4==4.12.3` / `4.13.3`: HTML/XML parser.
- `playwright==1.42.0` / `1.57.0`: Headless browser for JavaScript-heavy dynamic brand sites (e.g., Starbucks, McDonald's).
- `lxml==5.1.0` / `4.8.0`: High-performance XML/HTML parser.
- `httpx==0.28.1`, `selectolax==0.4.10`, `xmltodict==0.14.2`: Available in python environment.

### 2.2 Recommendation on Dependencies
No new external package installation is required. `requests`, `beautifulsoup4`, `lxml`, and `playwright` (all listed in `requirements.txt`) provide complete coverage for RSS parsing, web scraping, and fallback link verification.

---

## 3. Technical Design: Dynamic Real-Time Event Scraper Architecture

### 3.1 Multi-Tier Scraper Pipeline
To replace hardcoded strings with real-time dynamic data, the scraper will operate on a 3-tier pipeline:

```
[ Brand Target ]
      │
      ├───> Tier 1: Brand-Specific Live Parser (Starbucks, CU, GS25, Burger King, Olive Young, etc.)
      │        └── Dynamic HTML / JSON / Feed Scraping -> Real-time Title, Event Link, Description
      │
      ├───> Tier 2: Real-Time Multi-Source RSS & Search Aggregator
      │        └── Google News RSS / Open Search Feed -> Live Event Title, Article Link, Snippet
      │
      └───> Tier 3: Link Health Check & Graceful Fallback Manager (Req 4)
               └── Validates HTTP 200 OK for Event Page.
                   If 404/500/Timeout -> Fallback to Main Brand Landing Page URL.
```

### 3.2 Tier 1: Dedicated Brand Event Parsers
Implement specialized light parsers for major high-frequency brands:
1. **Convenience Stores (CU, GS25, Seven Eleven)**: Parse official monthly promo API/pages for current 1+1 / 2+1 campaign titles and links.
2. **Fast Food & Pizza (Burger King, McDonald's, Domino's, KFC)**: Scrape `/event` or `/promotion` list elements.
3. **Cafes & Bakeries (Starbucks, Paris Baguette, Mega Coffee)**: Leverage BeautifulSoup/Playwright to extract live event campaign titles.
4. **H&B / Department / Pop-ups (Olive Young, The Hyundai, Pop-up platforms)**: Extract current active event/popup titles and banners.

### 3.3 Tier 2: Real-Time RSS Feed Aggregator
For brands without dedicated parsers:
- Execute real-time RSS search using Google News RSS / Search Feed for `{Brand} + 이벤트 | 프로모션 | 할인 | 팝업` (filtered by `when:14d` or `when:30d`).
- Extract the latest headline as the dynamic event title.
- Parse item link and publication date.

### 3.4 Tier 3: Graceful Fallback Strategy (Requirement 4 Specification)
**Requirement**: "if an event page does not exist or fails to fetch, fallback to the main brand page URL gracefully."

**Implementation Strategy**:
```python
class FallbackUrlManager:
    @staticmethod
    def resolve_valid_event_url(event_url: str, main_brand_url: str) -> str:
        """
        Validates event_url via a fast HTTP HEAD/GET request.
        If event_url is missing, invalid, or returns 404/500/timeout,
        gracefully falls back to main_brand_url.
        """
        if not event_url or not event_url.startswith(("http://", "https://")):
            return main_brand_url

        try:
            # Fast header check (timeout=2s)
            resp = requests.head(event_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2, allow_redirects=True)
            if resp.status_code < 400:
                return event_url
        except Exception:
            pass

        # Fallback if HEAD request failed or wasn't supported
        try:
            resp = requests.get(event_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2, stream=True)
            if resp.status_code < 400:
                return event_url
        except Exception:
            pass

        # Graceful Fallback to Main Brand Page
        return main_brand_url
```

---

## 4. Proposed Interface & Data Model Contract

The enhanced scraper will return items conforming to this expanded dictionary interface:

```python
{
    "target": "스타벅스",
    "title": "[실시간 혜택] 2026 여름 e-프리퀀시 2차 프로모션",  # Dynamically scraped title
    "details": "https://www.starbucks.co.kr/whats_new/campaign_view.do?pro_seq=1234", # Fallback applied if invalid
    "category": "카페 및 베이커리/디저트",
    "description": "음료 17잔 적립 시 한정판 굿즈 증정 (행사기간: 07.15 ~ 08.15)",  # Real-time event description
    "status": "진행중",  # Event status
    "fallback_used": False  # Indicator if main page fallback was triggered
}
```

---

## 5. Verification & Test Plan

1. **Unit Testing (`tests/test_scraper_service.py`)**:
   - Verify `scrape()` returns dynamic event titles rather than hardcoded static titles.
   - Mock HTTP 404 response on event page to verify FallbackUrlManager returns main brand URL.
   - Verify all required fields (`target`, `title`, `details`, `category`) exist in returned dicts.
2. **URL Validity Testing (`tests/test_url_validity.py`)**:
   - Ensure 100% of returned `details` URLs return HTTP < 400 status codes.
   - Ensure zero `search.naver.com` landing URLs are generated.
3. **Pipeline & UI Integration Testing (`tests/test_main_pipeline.py`, `tests/test_usecases.py`)**:
   - Run full `pytest` suite across `tests/` directory to guarantee 100% pass and 0 side-effects.

---

## 6. Implementation Roadmap for Implementer

1. **Step 1**: Implement `FallbackUrlManager` class in `services/scraper_service.py`.
2. **Step 2**: Enhance `HybridOfficialScraper` to dynamically fetch live event titles and event URLs via Tier 1 brand parsers & Tier 2 RSS feeds.
3. **Step 3**: Wrap dynamic event URL resolution in `FallbackUrlManager.resolve_valid_event_url()`.
4. **Step 4**: Update unit tests in `tests/test_scraper_service.py` to assert dynamic title extraction and fallback handling.
5. **Step 5**: Execute `pytest` across all test files in `tests/` to verify zero regressions.
