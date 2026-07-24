from services.location_service import LocationService, _cached_search_nearby_brand, _cached_get_neighborhood

ls = LocationService()
# Search place for 태성로 107
lat, lon = ls.search_place("태성로 107")
print(f"태성로 107 coords: lat={lat}, lon={lon}")

if lat and lon:
    neighborhood = ls.get_neighborhood(lat, lon)
    print(f"Neighborhood: '{neighborhood}'")

    brands = ["CU", "GS25", "스타벅스", "이디야", "투썸플레이스", "맥도날드", "버거킹", "롯데리아", "올리브영", "다이소", "파리바게뜨", "치킨"]
    
    total_found_3km = 0
    for b in brands:
        res_3km = ls.search_nearby_brand(lat, lon, neighborhood, b, max_distance_km=3.0)
        print(f"Brand: {b} -> Found {len(res_3km)} items within 3.0km")
        for item in res_3km:
            print(f"   - {item['name']} ({item['distance_km']}km) | {item.get('address') or item.get('road_address')}")
        total_found_3km += len(res_3km)
        
    print(f"\nTotal items found across {len(brands)} sample brands within 3km: {total_found_3km}")
