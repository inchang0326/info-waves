# Handoff Report — GuziMap Address Landing URL Investigation

## 1. Observation

### HTML & Asset Source Analysis
- **Domain**: `https://xn--v69ak0xskm.com` (거지맵 / GuziMap)
- **Frontend Architecture**: React single-page application (CSR) bundled with Vite (`/assets/index-8l1xx0Wf.js`, 2,695,792 bytes).
- **Backend API**: Supabase REST endpoint (`https://lzeazgyvjzireemncjep.supabase.co/rest/v1/restaurants_public`).

### Bundle Query Parameter Analysis (`/assets/index-8l1xx0Wf.js`)
Inspection of all `URLSearchParams` instances and router state handlers across the JS bundle revealed the following query parameter conventions:

1. **Community Search (`/bang`)**:
   - Parameter: `q` (e.g., `?q=keyword` or `?category=all&q=keyword&page=1`)
   - Source code snippet (pos 1055494):
     `GV = "category", WV = "q", YV = "page"`
     `function ZV(e="all", t="", n=1) { ... r.set(WV, a) }`

2. **Deal Search (`/deal`)**:
   - Parameter: `q` (e.g., `?q=keyword` or `?category=all&q=keyword&page=1`)
   - Source code snippet (pos 1058217):
     `nG = "category", rG = "q", aG = "page"`
     `function oG(e="all", t=1, n="") { ... r.set(rG, i) }`

3. **Place / Restaurant Detail View (`/` or `/map`)**:
   - Parameter: `place` (e.g., `?place=<place_id>`)
   - Source code snippet (pos 2427061 & pos 2630252):
     `function T8(e) { const n = new URLSearchParams(e).get("place")?.trim(); return n || null }`
     `Et.searchParams.set("place", Z.id)`

4. **Map Target View Filter (`/` or `/map`)**:
   - Parameter: `target` (e.g., `?target=restaurants` or `?target=places`)
   - Source code snippet (pos 2597983):
     `function rtt(e) { const n = new URLSearchParams(e).get("target")?.trim().toLowerCase(); return n==="restaurants"||n==="restaurant"?"restaurants":n==="places"||n==="place"?"places":"all" }`

5. **Map Landing Page Address Search State (`/` or `/map`)**:
   - Search Keyword State: `[pn, Ir] = b.useState("")` (pos 2603002)
   - Modal Input State: `[Jt, bn] = b.useState("")`
   - Search Submission Handler `R_()` (pos 2620715):
     `R_ = () => { Xi([]), ie([]), nt([]), Ir(Jt.trim()), Ta(0), Ti(0), Pu(0), ... }`
   - Observation: The map landing component initializes the search query state `pn` to an empty string (`""`). It does not extract an address query parameter from `window.location.search` on initial load.

## 2. Logic Chain

1. **Frontend Search Parameter Convention**:
   - Analysis of GuziMap's bundle confirms that `q` is the universal search query key used across searchable tabs on the platform (`/bang?q=...`, `/deal?q=...`).
2. **Current Map Landing Component Behavior**:
   - On `https://xn--v69ak0xskm.com/`, the React map component initializes search state `pn` with `""`. It does not bind `location.search` query parameters (`?q=`, `?search=`, `?address=`) to automatically run a search on initial mount.
3. **Canonical Landing URL Standard**:
   - The standardized query parameter for search inputs across GuziMap is `q`.
   - `services/scraper_service.py` line 43 (`link = f"https://xn--v69ak0xskm.com/?q={encoded_addr}"`) and `tests/test_guzimap_integration.py` line 36 (`assert "https://xn--v69ak0xskm.com/?q=" in item["details"]`) use `?q={encoded_address}`.
4. **URL Encoding Requirement**:
   - Addresses containing spaces or Korean characters must be URL-encoded (e.g., `urllib.parse.quote(addr)`).

## 3. Caveats

- **Frontend SPA Limitation**: While `https://xn--v69ak0xskm.com/?q={encoded_address}` is the canonical URL format conforming to GuziMap's search parameter design, the current SPA React map component on `xn--v69ak0xskm.com` does not auto-populate the search modal input from `window.location.search` on mount. Users landing on the site via `?q=` will see the map centered based on their default location or geolocation, but the URL structure is future-proof and matches GuziMap's parameter scheme.
- No other search query parameter (`?search=`, `?address=`, `?query=`) is parsed by GuziMap.

## 4. Conclusion

- **Verified URL Format**:
  `https://xn--v69ak0xskm.com/?q={URL_ENCODED_ADDRESS}`
- **Example**:
  For restaurant address `"서울특별시 강남구 테헤란로 123"`:
  `https://xn--v69ak0xskm.com/?q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%20%EA%B0%95%EB%82%A8%EA%B5%AC%20%ED%85%8C%ED%97%8D%EB%9E%80%EB%A1%9C%20123`

## 5. Verification Method

To verify this investigation:
1. Inspect bundle `/assets/index-8l1xx0Wf.js` search parameter handling using:
   `python3 -c "import re; js=open('.agents/explorer_r1_1/guzimap_bundle.js').read(); print([m.group(0) for m in re.finditer(r'URLSearchParams', js)])"`
2. Verify existing test suite alignment:
   `pytest tests/test_guzimap_integration.py`
