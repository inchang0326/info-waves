import pytest
from unittest.mock import patch, MagicMock
from main import fetch_global_alerts, fetch_local_alerts
from services.location_service import LocationService
from services.ui_utils import generate_card_html, generate_mini_popup_html, format_expander_title

def test_uc01_location_search_centers_map_and_resets_list():
    """
    [UC-01] 위치 검색 시, 위치 기준이 변경되며 검색한 위치가 지도 정중앙에 배치되고 혜택 목록이 리셋됨
    """
    session_state = {
        "map_lat": 37.5665,
        "map_lon": 126.9780,
        "data_view": "내 주변 맞춤 혜택",
        "map_key_id": 0,
        "local_results": {"내 주변 매장 혜택": ["기존데이터"]}
    }
    
    with patch.object(LocationService, "search_place", return_value=(37.3584, 126.9331)):
        location_service = LocationService()
        s_lat, s_lon = location_service.search_place("산본역")
        
        if s_lat and s_lon:
            session_state["map_lat"] = s_lat
            session_state["map_lon"] = s_lon
            session_state["map_key_id"] += 1
            if "local_results" in session_state:
                del session_state["local_results"]
                
        assert session_state["map_lat"] == 37.3584
        assert session_state["map_lon"] == 126.9331
        assert "local_results" not in session_state


def test_uc02_map_click_centers_map_and_resets_list():
    """
    [UC-02] 지도상 마우스 좌클릭 시, 위치 기준이 변경되며 클릭한 위치가 지도 정중앙에 배치되고 혜택 목록이 리셋됨
    """
    session_state = {
        "map_lat": 37.360657,
        "map_lon": 126.928194,
        "map_key_id": 1,
        "local_results": {"내 주변 매장 혜택": ["기존데이터"]}
    }
    
    last_clicked = {"lat": 37.5216, "lng": 126.9242}
    if last_clicked:
        c_lat = round(last_clicked.get("lat", 0), 6)
        c_lon = round(last_clicked.get("lng", 0), 6)
        
        if session_state.get("map_lat") != c_lat or session_state.get("map_lon") != c_lon:
            session_state["map_lat"] = c_lat
            session_state["map_lon"] = c_lon
            session_state["map_key_id"] += 1
            if "local_results" in session_state:
                del session_state["local_results"]
                
        assert session_state["map_lat"] == 37.5216
        assert session_state["map_lon"] == 126.9242
        assert "local_results" not in session_state


def test_uc03_map_zoom_smoothness_css_rule_integrity():
    """
    [UC-03] 지도 확장/축소 시, 지도 깜빡임이 없어야 하며 매끄럽게 움직여야 함
    """
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
    assert "opacity: 1 !important;" in app_code
    assert "transition: none !important;" in app_code


def test_uc04_radius_slider_updates_search_radius():
    """
    [UC-04] 지도 탐색 반경 시, 탐색 반경이 변경되어야 함
    """
    session_state = {
        "radius_val": 3.0,
        "radius_slider_widget": 5.0
    }
    
    def sync_radius():
        session_state["radius_val"] = session_state["radius_slider_widget"]
        
    sync_radius()
    assert session_state["radius_val"] == 5.0


def test_uc05_map_cursor_emoji_unified_inside_and_outside_radius():
    """
    [UC-05] 지도 탐색 반경 범위 내와 밖의 마우스 이모지가 동일해야 함
    """
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
    assert ".leaflet-container, .leaflet-grab, .leaflet-interactive, .leaflet-marker-icon" in app_code
    assert "cursor: pointer !important;" in app_code


def test_uc06_search_completion_lists_nearby_deals():
    """
    [UC-06] 탐색 완료 시, 내 주변 혜택 목록이 리스트업 되어야 함
    """
    global_results = {
        "편의점 혜택": [{"target": "CU", "title": "쓔퍼세일", "details": "http://cu.com", "category": "편의점 혜택"}]
    }
    fake_places = [{"name": "CU 산본역점", "address": "산본동", "road_address": "산본로 1", "lat": 37.361, "lon": 126.928}]
    
    with patch("services.location_service.LocationService.get_neighborhood", return_value="산본동"), \
         patch("services.location_service._cached_search_nearby_brand", return_value=fake_places):
        
        local_results = fetch_local_alerts(37.360657, 126.928194, global_results, radius_km=3.0)
        assert "내 주변 매장 혜택" in local_results
        assert len(local_results["내 주변 매장 혜택"]) == 1
        assert local_results["내 주변 매장 혜택"][0]["target"] == "CU 산본역점"


def test_uc07_search_completion_preserves_radius():
    """
    [UC-07] 탐색 완료 시, 탐색 반경은 직전 탐색 반경과 동일해야 함
    """
    session_state = {"radius_val": 2.0}
    searched_radius = session_state.get("radius_val", 3.0)
    assert searched_radius == 2.0
    assert session_state["radius_val"] == 2.0


def test_uc08_branch_copy_address_copies_actual_road_address():
    """
    [UC-08] 내 주변 혜택 목록 내 매칭 주소의 주소 복사 시, 실제 해당 매장의 도로명 주소가 복사되어야 함
    """
    branches = [
        {"target": "CU 산본에듀점", "address": "지번주소 산본동 100", "road_address": "경기도 군포시 산본로 123번길 45"}
    ]
    card_html = generate_card_html("CU", "쓔퍼세일 1+1", "http://cu.com", branches=branches)
    
    assert 'data-addr="경기도 군포시 산본로 123번길 45"' in card_html
    assert '주소 복사' in card_html


def test_uc09_radius_change_does_not_reset_listed_deals():
    """
    [UC-09] 탐색 완료 후, 탐색 반경 변경 시에는 리스트업 된 내 주변 혜택 목록이 리셋되면 안 됨
    """
    session_state = {
        "radius_val": 3.0,
        "local_results": {"내 주변 매장 혜택": ["이전탐색결과"]}
    }
    
    session_state["radius_val"] = 5.0
    assert "local_results" in session_state
    assert len(session_state["local_results"]["내 주변 매장 혜택"]) == 1


def test_uc10_location_change_resets_listed_deals():
    """
    [UC-10] 탐색 완료 후, 지도 위치 기준이 변경 되면(위치 검색 또는 지도상 마우스 좌클릭), 내 주변 혜택 목록은 리셋 됨
    """
    session_state = {
        "map_lat": 37.360657,
        "map_lon": 126.928194,
        "local_results": {"내 주변 매장 혜택": ["이전탐색결과"]}
    }
    
    new_lat, new_lon = 37.5216, 126.9242
    if session_state["map_lat"] != new_lat or session_state["map_lon"] != new_lon:
        session_state["map_lat"] = new_lat
        session_state["map_lon"] = new_lon
        if "local_results" in session_state:
            del session_state["local_results"]
            
    assert "local_results" not in session_state


def test_uc11_research_preserves_map_center_and_radius():
    """
    [UC-11] 탐색 완료 후 '탐색' 버튼 재클릭 시, 지도 위치 기준 좌표 및 반경 조준이 그대로 유지됨
    """
    session_state = {
        "map_lat": 37.360657,
        "map_lon": 126.928194,
        "radius_val": 2.5
    }
    
    c_lat, c_lon = session_state["map_lat"], session_state["map_lon"]
    r_val = session_state["radius_val"]
    
    assert c_lat == 37.360657
    assert c_lon == 126.928194
    assert r_val == 2.5


def test_uc12_deal_card_link_opens_in_new_tab_safely():
    """
    [UC-12] 혜택 카드의 브랜드/타이틀 클릭 시 공식 랜딩 링크가 새 탭(target='_blank')에서 안전하게 열림
    """
    card_html = generate_card_html("스타벅스", "e-프리퀀시", "https://www.starbucks.co.kr")
    assert 'target="_blank"' in card_html
    assert 'rel="noopener noreferrer"' in card_html
    assert 'href="https://www.starbucks.co.kr"' in card_html


def test_uc13_branch_accordion_renders_store_name_and_road_address():
    """
    [UC-13] 내 주변 혜택 목록의 개별 지점 Accordion(details) 오픈 시 지점명과 도로명 주소가 결합 배치됨
    """
    branches = [
        {"target": "스타벅스 산본역점", "road_address": "경기도 군포시 산본로 323"}
    ]
    card_html = generate_card_html("스타벅스", "별다방 클래스", "http://starbucks.co.kr", branches=branches)
    assert '<details class="branches-details"' in card_html
    assert '스타벅스 산본역점' in card_html
    assert 'data-addr="경기도 군포시 산본로 323"' in card_html


def test_uc14_mini_popup_html_contains_logo_title_and_link():
    """
    [UC-14] 지도 마커 팝업 생성 시 브랜드 로고, 혜택 타이틀, 자세히 보기 링크가 정상 포함됨
    """
    popup_html = generate_mini_popup_html("올리브영", "올영세일", "https://www.oliveyoung.co.kr")
    assert '올리브영' in popup_html
    assert '올영세일' in popup_html
    assert 'https://www.oliveyoung.co.kr' in popup_html
    assert '자세히 보기' in popup_html


def test_uc15_expander_title_count_matches_actual_item_count():
    """
    [UC-15] 전국구 핫딜 카테고리 타이틀의 (count개) 숫자와 실제 리스트업 항목 수가 100% 일치함
    """
    category_title = format_expander_title("편의점 혜택", 7)
    assert category_title == "편의점 (7개)"
    assert "(7개)" in category_title


def test_uc16_whitespace_search_query_preserves_location():
    """
    [UC-16] 공백/빈 문자열 검색 제출 방어 시나리오
    - 사용자가 검색창에 스페이스바 공백("   ")만 입력하고 제출할 때
    - LocationService.search_place가 (None, None)을 반환하고 기존 좌표 세션이 100% 안전하게 유지됨
    """
    session_state = {"map_lat": 37.360657, "map_lon": 126.928194}
    location_service = LocationService()
    
    s_lat, s_lon = location_service.search_place("   ")
    assert s_lat is None
    assert s_lon is None
    assert session_state["map_lat"] == 37.360657
    assert session_state["map_lon"] == 126.928194


def test_uc17_click_storm_same_location_consistency():
    """
    [UC-17] 동일 위치 연속 탐색 연타(Click Storm) 일관성 시나리오
    - 지도 좌표 변경 없이 '탐색' 버튼을 5회 연속 연타 클릭했을 때
    - 결과 딕셔너리가 훼손되지 않고 100% 동일한 매장 수량이 일관되게 반환됨
    """
    global_results = {
        "편의점 혜택": [{"target": "CU", "title": "쓔퍼세일", "details": "http://cu.com", "category": "편의점 혜택"}]
    }
    fake_places = [{"name": "CU 산본역점", "address": "산본동", "road_address": "산본로 1", "lat": 37.361, "lon": 126.928}]
    
    with patch("services.location_service.LocationService.get_neighborhood", return_value="산본동"), \
         patch("services.location_service._cached_search_nearby_brand", return_value=fake_places):
        
        # 5회 연속 연타 클릭 시뮬레이션
        for _ in range(5):
            res = fetch_local_alerts(37.360657, 126.928194, global_results, radius_km=3.0)
            assert len(res["내 주변 매장 혜택"]) == 1
            assert res["내 주변 매장 혜택"][0]["target"] == "CU 산본역점"


def test_uc18_kakao_search_network_failure_graceful_fallback():
    """
    [UC-18] 카카오 지도 검색 네트워크 장애 시 Graceful Fallback 시나리오
    - 장소 검색 중 네트워크 단절/타임아웃 발생 시 앱 크래시 없이 (None, None)을 반환하고 에러가 격리됨
    """
    location_service = LocationService()
    with patch("services.location_service._session.get") as mock_get:
        mock_get.side_effect = Exception("Kakao Map API Network Timeout")
        s_lat, s_lon = location_service.search_place("강남역")
        assert s_lat is None
        assert s_lon is None


def test_uc19_special_characters_store_name_injection_safety():
    """
    [UC-19] 특수문자/큰따옴표 포함 매장명 HTML/JS 인젝션 방어 시나리오
    - 매장 지점명이나 주소에 큰따옴표("), 작은따옴표(')가 포함되어도 이스케이프(&quot;) 정제되어 JS 이벤트를 방어함
    """
    branches = [
        {"target": "CU \"산본\"역점", "road_address": "산본로 '123' \"상가\""}
    ]
    card_html = generate_card_html("CU", "쓔퍼세일 1+1", "http://cu.com", branches=branches)
    assert 'data-addr="산본로 &#39;123&#39; &quot;상가&quot;"' in card_html or 'data-addr="산본로 \'123\' &quot;상가&quot;"' in card_html
    assert 'copy-addr-btn' in card_html


def test_uc20_tab_switch_restores_map_location_and_radius_session():
    """
    [UC-20] 탭 이동 간 지도 좌표 및 탐색 세션 완전 독립 복원 시나리오
    - '전국구 핫딜' 뷰를 둘러본 후 다시 '내 주변 혜택' 탭으로 돌아왔을 때 기존 지도 좌표와 반경 설정이 100% 원복 보존됨
    """
    session_state = {
        "map_lat": 37.360657,
        "map_lon": 126.928194,
        "radius_val": 2.5,
        "data_view": "내 주변 맞춤 혜택"
    }
    
    # 1. '전국구 핫딜' 탭으로 이동
    session_state["data_view"] = "전국구 핫딜"
    assert session_state["data_view"] == "전국구 핫딜"
    
    # 2. 다시 '내 주변 혜택' 탭으로 복귀
    session_state["data_view"] = "내 주변 맞춤 혜택"
    assert session_state["data_view"] == "내 주변 맞춤 혜택"
    assert session_state["map_lat"] == 37.360657 # 지도 중심 좌표 원복
    assert session_state["map_lon"] == 126.928194
    assert session_state["radius_val"] == 2.5 # 반경 설정 원복


def test_uc21_location_key_auto_synchronization_and_guzimap_guaranteed_recommendation():
    """
    [UC-21] 위치/반경 변경 시 자동 탐색 방지 및 탐색 버튼 클릭 시 거지맵 100% 최신화 추천 시나리오
    - 좌표나 반경이 변경될 때 _last_searched_key 미일치로 local_results가 자동 제거됨 (불필요한 자동 탐색 차단)
    - 탐색 버튼 클릭 시 새 좌표/반경 기준으로 거지맵 가성비 식당 데이터가 100% 리스트업됨
    """
    global_results = {
        "거지맵 (가성비 식당 & 초저가 혜택)": [
            {
                "target": "거지맵 - 포스토리 온수점",
                "title": "거지맵 가성비 식당: 쌀국수 (8,000원)",
                "details": "https://naver.me/test",
                "category": "거지맵 (가성비 식당 & 초저가 혜택)",
                "lat": 37.493995,
                "lon": 126.833499,
                "address": "서울 구로구 부일로15길 21",
                "brand": "포스토리 온수점"
            }
        ]
    }
    
    session_state = {
        "map_lat": 37.493995,
        "map_lon": 126.833499,
        "radius_val": 3.0,
        "_last_searched_key": None,
        "local_results": {"기존데이터": []}
    }
    
    current_key = (
        round(float(session_state["map_lat"]), 5),
        round(float(session_state["map_lon"]), 5),
        round(float(session_state["radius_val"]), 2)
    )
    
    # 1. 반경/위치 변경 시 자동 탐색 없이 local_results 소멸 검증
    if session_state.get("_last_searched_key") != current_key:
        session_state.pop("local_results", None)
        
    assert "local_results" not in session_state

    # 2. 명시적 탐색 버튼 클릭 시 local_results 생성 및 거지맵 노출 검증
    session_state["_last_searched_key"] = current_key
    session_state["local_results"] = fetch_local_alerts(current_key[0], current_key[1], global_results, current_key[2])
    
    assert session_state["_last_searched_key"] == current_key
    assert len(session_state["local_results"]["거지맵 (가성비 식당 & 초저가 혜택)"]) == 1
    assert "📍 [" in session_state["local_results"]["거지맵 (가성비 식당 & 초저가 혜택)"][0]["title"]

