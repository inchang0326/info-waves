import sys
sys.path.insert(0, '.')

from services.location_service import LocationService

ls = LocationService()

test_cases = [
    ("고산로 517번길 20", "산본동", 3.0),
    ("태성로 107", "태전동", 3.0),
    ("판교역", "백현동", 3.0)
]

brands = ["CU", "GS25", "스타벅스", "맥도날드", "버거킹", "올리브영", "파리바게뜨", "도미노피자", "교촌치킨", "노모어피자"]

for place, expected_dong, radius in test_cases:
    lat, lon = ls.search_place(place)
    print(f"\n================ LOCATION: '{place}' (lat={lat}, lon={lon}) ================")
    if lat and lon:
        nb = ls.get_neighborhood(lat, lon)
        print(f"Extracted Neighborhood: '{nb}'")
        total_found = 0
        for b in brands:
            stores = ls.search_nearby_brand(lat, lon, nb, b, max_distance_km=radius)
            total_found += len(stores)
            print(f"  Brand [{b:<10}]: Found {len(stores)} stores within {radius}km")
        print(f"TOTAL STORES FOR {len(brands)} BRANDS: {total_found}")
