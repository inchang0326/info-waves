import sys
sys.path.insert(0, '.')

from services.location_service import LocationService
from main import fetch_global_alerts, fetch_local_alerts

service = LocationService()
global_results = fetch_global_alerts()

lat, lon = service.search_place("태성로 107")
print(f"태성로 107 -> lat={lat}, lon={lon}")

if lat and lon:
    local_res = fetch_local_alerts(lat, lon, global_results, radius_km=3.0)
    total_items = 0
    cat_counts = {}
    for cat, items in local_res.items():
        if cat != "내 주변 매장 혜택":
            cat_counts[cat] = len(items)
            total_items += len(items)
            print(f"Category [{cat}]: {len(items)} items")
    print(f"\nTOTAL ITEMS RETURNED AT 3.0KM FOR 태성로 107: {total_items}")
