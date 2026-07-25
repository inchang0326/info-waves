import pytest
from services.ui_utils import get_brand_logo, get_brand_fallback_badge
from services.location_service import LocationService
from main import fetch_global_alerts, fetch_local_alerts

def test_requirement_1_brand_logos_not_universe_fallback():
    """
    [Req 1] 할리스, 천년닭강정, 60계치킨, 동대문엽기떡볶이, 한솥도시락, 신전떡볶이, 역전할머니맥주, GS더프레시, 무인양품, 롯데월드
    1) 고유 로고 (또는 명확한 SVG 배지)를 반환해야 함.
    2) 구글 s2/favicons의 기본 우주/지구본 로고로 반환되어서는 안 됨.
    3) fallback_badge는 브랜드명이 명시된 Base64 SVG 배지여야 함.
    """
    target_brands = [
        "할리스", "천년닭강정", "60계치킨", "동대문엽기떡볶이", "한솥도시락",
        "신전떡볶이", "역전할머니맥주", "GS더프레시", "무인양품", "롯데월드"
    ]
    
    for brand in target_brands:
        logo_url = get_brand_logo(brand)
        fallback_url = get_brand_fallback_badge(brand)
        
        # Must not fall back to Google's default blue globe favicons
        assert "google.com/s2/favicons" not in logo_url, f"Brand {brand} must not use Google favicon service"
        
        # Must return valid URL or Base64 SVG
        assert logo_url.startswith("http://") or logo_url.startswith("https://") or logo_url.startswith("data:image/svg+xml;base64,"), \
            f"Logo URL for {brand} is invalid: {logo_url}"
            
        # Fallback badge must be explicit Base64 SVG
        assert fallback_url.startswith("data:image/svg+xml;base64,"), \
            f"Fallback badge for {brand} must be Base64 SVG"


def test_requirement_2_location_search_component_trigger_logic():
    """
    [Req 2] 위치 검색 시 handle_search()가 fetch_local_alerts()를 바로 호출하지 않고,
    '탐색' 버튼을 클릭했을 때만 주변 혜택 목록이 리스트업되는 구조인지 검증
    """
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
        
    # handle_search() definition should pop local_results and rerun, NOT call fetch_local_alerts
    handle_search_start = app_code.find("def handle_search():")
    assert handle_search_start != -1
    
    handle_search_end = app_code.find("def set_view_local():", handle_search_start)
    handle_search_code = app_code[handle_search_start:handle_search_end]
    
    assert "fetch_local_alerts" not in handle_search_code, \
        "handle_search() in app.py must NOT call fetch_local_alerts automatically!"
    assert 'st.session_state.pop("local_results", None)' in handle_search_code, \
        "handle_search() in app.py must clear local_results until Explore button is clicked"


def test_requirement_3_taeseong_and_nationwide_store_richness():
    """
    [Req 3] 태성로 107 및 전국 주요 지역 3km 반경 검색 시 5개 제한 없이 수십 개의 매장이 풍부하게 검색되는지 검증
    """
    ls = LocationService()
    global_data = fetch_global_alerts()
    
    # 1. Test 태성로 107 specifically
    lat, lon = ls.search_place("태성로 107")
    assert lat is not None and lon is not None, "Failed to geocode 태성로 107"
    
    local_res = fetch_local_alerts(lat, lon, global_data, radius_km=3.0)
    all_stores = local_res.get("내 주변 매장 혜택", [])
    total_stores = len(all_stores)
    print(f"Total stores found for 태성로 107 within 3km: {total_stores}")
    assert total_stores >= 20, f"Expected >= 20 stores for 태성로 107, but got {total_stores}"
    
    # 2. Test nationwide key regions
    nationwide_test_places = ["고산로 517번길 20", "판교역", "강남역"]
    for place in nationwide_test_places:
        p_lat, p_lon = ls.search_place(place)
        if p_lat and p_lon:
            res = fetch_local_alerts(p_lat, p_lon, global_data, radius_km=3.0)
            st_count = len(res.get("내 주변 매장 혜택", []))
            print(f"Total stores found for {place} within 3km: {st_count}")
            assert st_count >= 20, f"Expected >= 20 stores for {place}, but got {st_count}"
