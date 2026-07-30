# Project: Info Waves - GuziMap Address Landing URL Update

## Architecture
- Info Waves application for searching location-based popup stores and cheap restaurant/event info.
- Services:
  - `services/scraper_service.py`: Scrapes event info and handles GuziMap landing URL generation (`GuziMapScraper`).
  - `services/location_service.py`: Handles location searching, kakao queries, cache, and popup store details.
  - `app.py`: Streamlit / Web UI for searching and displaying popup stores/restaurants on map and list view.
  - `main.py`: Entrypoint / core logic integration.
  - `tests/`: Automated pytest test suite (85 tests).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1_GuziMap_URL_Analysis | Analyze GuziMap website/source (`https://xn--v69ak0xskm.com`) URL parameter structure for address search | None | IN_PROGRESS |
| 2 | M2_GuziMapScraper_Update | Remove Naver Place fallback in `GuziMapScraper`, update landing URL with address search parameter, and update test suite | M1 | PLANNED |
| 3 | M3_Verification_Audit | Review, Challenge, and Forensic Integrity Audit to ensure 85/85 pytest pass & landing accuracy | M2 | PLANNED |

## Interface Contracts
### scraper_service ↔ location_service / app
- `GuziMapScraper.scrape()` / landing link generator must return GuziMap URL pre-populated with address parameter (no Naver Place redirect).
- `details` URL opens GuziMap with address auto-filled and search results displayed.

## Code Layout
- `services/scraper_service.py`: GuziMapScraper logic and landing URL creation.
- `tests/test_guzimap_integration.py`: Integration tests for GuziMapScraper.
- `tests/`: Entire test suite (85 tests total).
