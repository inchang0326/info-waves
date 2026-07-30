# Handoff Report — Explorer 2: GuziMapScraper Codebase Inspection & Landing URL Analysis

## 1. Observation

- **File Path**: `/Users/steady/.openclaw/workspace/info_waves/services/scraper_service.py`
- **Class Identified**: `GuziMapScraper` (lines 18–58)
  ```python
  18: class GuziMapScraper(AbstractScraper):
  19:     def __init__(self):
  20:         super().__init__("거지맵 (저예산 식당 & 초저가 혜택)")
  21: 
  22:     def scrape(self) -> List[Dict[str, str]]:
  23:         url = "https://lzeazgyvjzireemncjep.supabase.co/rest/v1/restaurants_public?select=*"
  24:         supabase_key = os.getenv("GUZIMAP_API_KEY") or os.getenv("SUPABASE_KEY") or "sb_publishable_b7EOyF1IuulD2ZU-VYqtCA_2L3X6PSV"
  25:         headers = {
  26:             "apikey": supabase_key,
  27:             "Authorization": f"Bearer {supabase_key}",
  28:             "User-Agent": "Mozilla/5.0"
  29:         }
  30:         results = []
  31:         try:
  32:             resp = requests.get(url, headers=headers, timeout=6)
  33:             if resp.status_code == 200:
  34:                 data = resp.json()
  35:                 for r in data:
  36:                     name = r.get("name")
  37:                     if not name: continue
  38:                     menu = r.get("latest_menu_name") or "가성비 식단"
  39:                     price = r.get("latest_price_krw")
  40:                     price_str = f" ({price:,}원)" if price else ""
  41:                     addr = r.get("address", "")
  42:                     encoded_addr = urllib.parse.quote(addr)
  43:                     link = f"https://xn--v69ak0xskm.com/?q={encoded_addr}"
  44:                     title = f"거지맵 가성비 식당: {menu}{price_str} | {addr}"
  45:                     
  46:                     results.append({
  47:                         "target": f"거지맵 - {name}",
  48:                         "title": title,
  49:                         "details": link,
  50:                         "category": "거지맵 (가성비 식당 & 초저가 혜택)",
  51:                         "lat": float(r.get("lat")) if r.get("lat") else None,
  52:                         "lon": float(r.get("lng")) if r.get("lng") else None,
  53:                         "address": addr,
  54:                         "brand": name
  55:                     })
  56:         except Exception as e:
  57:             logger.exception(f"GuziMap scraping failed: {e}")
  58:         return results
  ```
- **Merging Location**: `HybridOfficialScraper.scrape()` at lines 450–456:
  ```python
  450:         # 거지맵 병합
  451:         try:
  452:             guzi_items = GuziMapScraper().scrape()
  453:             if guzi_items:
  454:                 results.extend(guzi_items)
  455:         except Exception as e:
  456:             logger.exception(f"GuziMap fetch error: {e}")
  ```
- **Naver Place Code Locations**:
  - `NaverPlaceDirectScraper` (lines 60–91): Scrapes `https://m.map.naver.com/search2/search.naver?query={self.query}` for general Naver Place queries.
  - `FallbackUrlManager` (lines 179–217): Health-checks URLs and falls back to main landing page URLs if HTTP status >= 400.
  - Supabase restaurant records contain `naver_place_id` (e.g. `"naver_place_id": "12345678"` in mock datasets), which in legacy iterations was used to build Naver Place redirect URLs (`https://m.place.naver.com/place/...`).

## 2. Logic Chain

1. **Current Landing URL Mechanism**:
   - `GuziMapScraper` fetches restaurant records from Supabase (`restaurants_public`).
   - Line 41 retrieves the address using `addr = r.get("address", "")`.
   - Line 42 URL-encodes the address using `encoded_addr = urllib.parse.quote(addr)`.
   - Line 43 generates the landing link as `link = f"https://xn--v69ak0xskm.com/?q={encoded_addr}"`.

2. **Naver Place Fallback / Redirection Removal**:
   - In legacy code or potential fallback paths, missing addresses or presence of `naver_place_id` caused items to redirect to Naver Place (`map.naver.com` or `search.naver.com`).
   - The current `GuziMapScraper` implementation already generates `https://xn--v69ak0xskm.com/?q=...` directly, but needs defensive handling for edge cases (e.g. `r.get("address")` returning `None` instead of string, or empty address string).

3. **Defensive Edge Case Analysis**:
   - If `r` contains `"address": None`, calling `r.get("address", "")` returns `None`. Passing `None` to `urllib.parse.quote()` raises `TypeError: expected string or bytes-like object`.
   - Using `addr = r.get("address") or ""` ensures `addr` is always a string.
   - If `addr` is non-empty, `encoded_addr = urllib.parse.quote(addr)` produces `https://xn--v69ak0xskm.com/?q={encoded_addr}`.
   - If `addr` is empty, `link` can fall back to `https://xn--v69ak0xskm.com` (or `https://xn--v69ak0xskm.com/?q=`), completely avoiding any Naver Place URL generation.

4. **Integration Verification**:
   - `HybridOfficialScraper.scrape()` calls `GuziMapScraper().scrape()` and appends results directly without altering the `details` field.
   - All returned items retain `details` pointing to `https://xn--v69ak0xskm.com/?q=...`, satisfying `test_url_validity.py`'s rule that zero `search.naver.com` URLs exist in scraped alerts.

## 3. Caveats

- **Supabase Field Nullability**: Supabase API responses may contain `null` for the `address` key in some records. Using `r.get("address") or ""` prevents potential `NoneType` errors.
- **URL Encoding**: Multi-byte Korean address strings (e.g. `"경기도 군포시 광정로 68"`) must be URL-encoded using `urllib.parse.quote()` so browsers can navigate correctly without encoding issues.
- **No Source Code Edit Permission**: This report is read-only analysis. Implementation of refactoring must be performed by the Implementer agent.

## 4. Conclusion

`GuziMapScraper` in `services/scraper_service.py` is structured to construct landing URLs using the query parameter format `https://xn--v69ak0xskm.com/?q={encoded_addr}`.

To guarantee zero Naver Place fallbacks and bulletproof execution:
1. Ensure `addr = r.get("address") or ""` handles `None` values safely.
2. Build `link = f"https://xn--v69ak0xskm.com/?q={urllib.parse.quote(addr)}"` when `addr` is present, or `https://xn--v69ak0xskm.com` when `addr` is empty.
3. Ensure no fallback logic introduces `map.naver.com` or `search.naver.com` URLs for GuziMap items.

## 5. Verification Method

1. **Code Inspection**:
   View `services/scraper_service.py` lines 18–58 to confirm `GuziMapScraper` URL generation logic.
2. **Pytest Verification**:
   Run `pytest tests/test_guzimap_integration.py` and `pytest tests/test_url_validity.py` to confirm GuziMap landing URL format assertions and absence of Naver search links.
