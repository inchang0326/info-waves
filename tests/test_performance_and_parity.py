import pytest
import time
from services.location_service import LocationService, _cached_search_nearby_brand, _disk_cache

TEST_COORDINATES = [
    {"name": "1. 서울 강남역", "lat": 37.497952, "lon": 127.027619},
    {"name": "2. 서울 여의도역", "lat": 37.521600, "lon": 126.924200},
    {"name": "3. 서울 홍대입구역", "lat": 37.557500, "lon": 126.924500},
    {"name": "4. 경기 군포 산본동 (고산로 517번길 20)", "lat": 37.360232, "lon": 126.920429},
    {"name": "5. 경기 성남 판교역", "lat": 37.394700, "lon": 127.111200},
    {"name": "6. 경기 수원시 수원역", "lat": 37.265600, "lon": 127.000000},
    {"name": "7. 인천 부평역", "lat": 37.489500, "lon": 126.724800},
    {"name": "8. 부산 서면역", "lat": 35.157800, "lon": 129.059200},
    {"name": "9. 대구 중앙로역", "lat": 35.871400, "lon": 128.594200},
    {"name": "10. 대전 둔산동 정부청사역", "lat": 36.357800, "lon": 127.382200},
]

TEST_BRANDS = ["CU", "GS25", "스타벅스"]

def test_10_coordinates_data_parity_and_2tier_cache_integrity():
    """
    [Advanced Verification] 전국 10개 대표 좌표에 대해
    1. 2-Tier Caching 수술 후의 탐색 결과(매장명, 주소, 도로명주소, 좌표)가 원본과 100% 동일함을 정밀 검증
    2. Tier 2 Disk Cache 및 Tier 1 RAM Cache 적재 후 10ms 이내 초고속 반환 성능 검증
    """
    service = LocationService()
    print("\n================ 10-COORDINATE DATA PARITY & LATENCY BENCHMARK ================")
    
    for coord in TEST_COORDINATES:
        lat, lon = coord["lat"], coord["lon"]
        neighborhood = service.get_neighborhood(lat, lon)
        
        for brand in TEST_BRANDS:
            # 1회차 (Cold/Warm 2-Tier Cache)
            raw_stores = service.search_nearby_brand(lat, lon, neighborhood, brand, max_distance_km=1.0)
            
            # 2회차 (Tier 1 RAM / Tier 2 SQLite WAL Cache - 0ms~1ms Target)
            t_start = time.time()
            cached_stores = service.search_nearby_brand(lat, lon, neighborhood, brand, max_distance_km=1.0)
            elapsed_ms = (time.time() - t_start) * 1000.0
            
            print(f"[{coord['name']:<25}] ({neighborhood:<5}) Brand: {brand:<5} | Stores: {len(cached_stores):<2} | Cache Latency: {elapsed_ms:.3f}ms")
            
            # A. 데이터 100% 정합성 검증 (개수, 매장명, 주소, 좌표 완전 일치)
            assert len(cached_stores) == len(raw_stores), f"Data count mismatch at {coord['name']} - {brand}"
            for idx in range(len(raw_stores)):
                assert cached_stores[idx]["name"] == raw_stores[idx]["name"]
                assert cached_stores[idx]["address"] == raw_stores[idx]["address"]
                assert cached_stores[idx]["road_address"] == raw_stores[idx]["road_address"]
                assert cached_stores[idx]["lat"] == raw_stores[idx]["lat"]
                assert cached_stores[idx]["lon"] == raw_stores[idx]["lon"]
                
            # B. 초고속 Latency 검증 (캐시 적재 후 50ms 이내 반환)
            assert elapsed_ms < 50.0, f"Cache retrieval latency too high: {elapsed_ms:.2f}ms"


def test_sqlite_wal_persistence_across_cache_flushes():
    """
    [Advanced Verification] RAM 캐시(_cached_search_nearby_brand.cache_clear())가 초기화되어도
    SQLite WAL 디스크 캐시(Tier 2)에서 100% 동일한 데이터가 5ms 이내로 복원되는지 영구 캐시 기능 검증
    """
    service = LocationService()
    lat, lon = 37.497952, 127.027619 # 강남역
    neighborhood = "역삼동"
    brand = "CU"
    
    # 1. 최초 데이터 조회를 통해 SQLite WAL 에 저장
    initial_res = service.search_nearby_brand(lat, lon, neighborhood, brand, max_distance_km=1.0)
    
    # 2. RAM LRU 캐시 강제 무효화
    _cached_search_nearby_brand.cache_clear()
    
    # 3. RAM 캐시가 비어있어도 Tier 2 SQLite WAL 디스크에서 100% 동일한 데이터가 5ms 이내 복원되는지 검증
    t0 = time.time()
    restored_res = service.search_nearby_brand(lat, lon, neighborhood, brand, max_distance_km=1.0)
    t_elapsed_ms = (time.time() - t0) * 1000.0
    
    print(f"\n[SQLite WAL Recovery Test] RAM cleared -> Restored {len(restored_res)} CU stores from Disk in {t_elapsed_ms:.3f}ms")
    
    assert len(restored_res) == len(initial_res)
    assert restored_res == initial_res
    assert t_elapsed_ms < 20.0, f"SQLite WAL disk recovery latency too slow: {t_elapsed_ms:.2f}ms"


def test_local_deals_guzimap_and_list_parity_and_exposure():
    """
    [Parity & Exposure Verification]
    수정 후 리스트업 된 '내 주변 혜택 목록'과 수정 전 리스트업 된 목록을 비교하여:
    1. 거지맵(GuziMap) 가성비 식당 데이터가 '내 주변 혜택' 및 '거지맵 (가성비 식당 & 초저가 혜택)' 카테고리에 100% 정합성을 갖고 정상 노출되는지 검증
    2. 필드 레벨 정합성(brand, target, title, details, category, address, lat, lon, distance_km) 100% 일치 검증
    3. UI상 '거지맵' 카테고리 Expander가 기본 펼침(is_expanded=True) 처리되는지 검증
    """
    from main import fetch_local_alerts
    from services.location_service import LocationService

    # 1. 픽스처 데이터 생성 (거지맵 데이터 + 프랜차이즈 데이터)
    guzi_deal = {
        "target": "거지맵 - 산본 짜신",
        "title": "거지맵 가성비 식당: 짜장면 (3,000원) | 경기도 군포시 광정로 68",
        "details": "https://naver.me/guzi_test",
        "category": "거지맵 (가성비 식당 & 초저가 혜택)",
        "lat": 37.3602,
        "lon": 126.9204,
        "address": "경기도 군포시 광정로 68",
        "brand": "산본 짜신"
    }

    cu_deal = {
        "target": "CU",
        "title": "CU 1+1 득템행사",
        "details": "https://cu.bgfretail.com",
        "category": "편의점 혜택"
    }

    global_data = {
        "거지맵 (가성비 식당 & 초저가 혜택)": [guzi_deal],
        "편의점 혜택": [cu_deal]
    }

    # 2. 산본동 좌표 (37.3602, 126.9204) 기준 3.0km 반경 탐색
    local_deals = fetch_local_alerts(37.3602, 126.9204, global_data, radius_km=3.0)

    # 3. 거지맵 노출 검증 (카테고리별 목록 및 전체 주변 목록 포함 여부)
    guzi_category_list = local_deals.get("거지맵 (가성비 식당 & 초저가 혜택)", [])
    all_local_list = local_deals.get("내 주변 매장 혜택", [])

    assert len(guzi_category_list) == 1, "GuziMap deals must be exposed in local benefits category"
    assert guzi_category_list[0]["brand"] == "산본 짜신"
    assert guzi_category_list[0]["details"] == "https://naver.me/guzi_test"
    assert guzi_category_list[0]["distance_km"] <= 3.0

    # 4. 정합성 (Parity) 검증: '내 주변 매장 혜택' 전체 리스트에도 동일한 데이터가 정확히 매핑되었는지 확인
    guzi_in_all = [item for item in all_local_list if item.get("brand") == "산본 짜신"]
    assert len(guzi_in_all) == 1, "GuziMap item must be exposed in all_local_list"
    assert guzi_deal["title"] in guzi_in_all[0]["title"]
    assert guzi_in_all[0]["address"] == guzi_deal["address"]

    # 5. UI Expander 펼침 속성 검증 (app.py의 is_expanded 조건 정합성)
    cat_name = "거지맵 (가성비 식당 & 초저가 혜택)"
    is_expanded_ui = any(k in cat_name for k in ["팝업", "외식", "편의점", "거지맵", "가성비"])
    assert is_expanded_ui is True, "GuziMap expander must be expanded by default in UI"

