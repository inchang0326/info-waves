import sys
import requests
import json
import math

# Add workspace to path
sys.path.insert(0, '/Users/steady/.openclaw/workspace/info_waves')

from services.location_service import LocationService
from main import fetch_global_alerts, fetch_local_alerts

ls = LocationService()
lat, lon = ls.search_place("고산로 517번길 20")
print(f"Place '고산로 517번길 20': lat={lat}, lon={lon}")

if lat and lon:
    global_results = fetch_global_alerts()
    print("Global results categories:", {k: len(v) for k, v in global_results.items()})
    
    local_res = fetch_local_alerts(lat, lon, global_results, radius_km=3.0)
    print("\n--- 3.0km Local Alerts Results ---")
    total_local = 0
    for cat, items in local_res.items():
        if cat != "내 주변 매장 혜택":
            print(f"Category [{cat}]: {len(items)} items")
            total_local += len(items)
            for item in items[:2]:
                print(f"   - {item.get('brand')} / {item.get('target')} | {item.get('road_address') or item.get('address')}")
    print(f"\nTOTAL LOCAL ITEMS AT 3.0KM: {total_local}")
