import sys
sys.path.insert(0, '.')

from services.location_service import LocationService
from services.ui_utils import get_brand_logo
from main import fetch_global_alerts, fetch_local_alerts

print("==================================================")
print("1. BRAND LOGO RESOLUTION VERIFICATION")
print("==================================================")
problem_brands = [
    "할리스", "천년닭강정", "60계치킨", "동대문엽기떡볶이", "한솥도시락",
    "신전떡볶이", "역전할머니맥주", "GS더프레시", "무인양품", "롯데월드"
]
all_logos_ok = True
for b in problem_brands:
    logo = get_brand_logo(b)
    is_base64_svg = logo.startswith("data:image/svg+xml;base64,")
    print(f"Brand [{b:<12}]: {'✅ Base64 SVG (Prism Crisp 100%)' if is_base64_svg else '❌ FAILED'}")
    if not is_base64_svg:
        all_logos_ok = False

print(f"\nLogo Test Overall: {'✅ PASSED (All 10 brands render crisp Base64 vector SVGs)' if all_logos_ok else '❌ FAILED'}")

print("\n==================================================")
print("2. LOCATION SEARCH & NATIONWIDE COVERAGE VERIFICATION")
print("==================================================")
ls = LocationService()
global_data = fetch_global_alerts()

test_queries = [
    ("고산로 517번길 20", 3.0),
    ("태성로 107", 3.0),
    ("판교역", 3.0)
]

all_locations_ok = True
for query, r in test_queries:
    lat, lon = ls.search_place(query)
    print(f"\n--- Testing Query: '{query}' (Radius: {r}km) ---")
    print(f"Coordinates: lat={lat}, lon={lon}")
    if not lat or not lon:
        print(f"❌ Failed to geocode '{query}'")
        all_locations_ok = False
        continue
        
    local_res = fetch_local_alerts(lat, lon, global_data, radius_km=r)
    total_items = 0
    cat_counts = {}
    for cat, items in local_res.items():
        if cat != "내 주변 매장 혜택" and items:
            cat_counts[cat] = len(items)
            total_items += len(items)
            
    print(f"Total stores found: {total_items}")
    print("Categories summary:", cat_counts)
    if total_items < 20:
        print(f"❌ FAIL: Low item count ({total_items}) for '{query}'")
        all_locations_ok = False
    else:
        print(f"✅ PASS: Rich store list ({total_items} items found)")

print("\n==================================================")
print(f"FINAL VERIFICATION RESULT: {'🎉 ALL TESTS PASSED SUCCESSFULLY!' if (all_logos_ok and all_locations_ok) else '❌ FAILURES DETECTED'}")
print("==================================================")
