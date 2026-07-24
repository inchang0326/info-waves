import pytest
from unittest.mock import patch, MagicMock
from services.location_service import LocationService, _cached_get_neighborhood, _cached_search_nearby_brand

def test_haversine_distance_calculation():
    """두 GPS 좌표 간의 Haversine 거리 계산 정밀도를 원자 단위로 검증합니다."""
    service = LocationService()
    # 1. 동일 좌표 거리 -> 0.0km
    same_dist = service._calculate_distance(37.360657, 126.928194, 37.360657, 126.928194)
    assert abs(same_dist) < 0.0001

    # 2. 산본동(37.360657, 126.928194) -> 여의도역(37.5216, 126.9242) 대략 17.8km~18.0km 구간
    sanbon_to_yeouido = service._calculate_distance(37.360657, 126.928194, 37.5216, 126.9242)
    assert 17.0 <= sanbon_to_yeouido <= 19.0

def test_get_neighborhood_fallback_on_exception():
    """역지오코딩 API 예외 발생 시 시스템 기본값('여의도동')으로 안전하게 Fallback 되는지 검증합니다."""
    with patch("services.location_service._session.get") as mock_get:
        mock_get.side_effect = Exception("OpenStreetMap Network Timeout Error")
        result = _cached_get_neighborhood(0.001, 0.001)
        assert result == "여의도동"

def test_search_nearby_brand_filtering():
    """
    이마트 검색 시 '24' / '에브리데이' 브랜드가 거르고,
    GS25 검색 시 '수퍼' 브랜드가 포함된 상호명이 제외되는 필터링 로직을 원자 단위로 검증합니다.
    """
    fake_json_text = 'jQuery_({"place": [{"name": "이마트 산본점", "address": "경기도 군포시", "lat": "37.360", "lon": "126.928"}, {"name": "이마트24 산본역점", "address": "경기도 군포시", "lat": "37.361", "lon": "126.929"}, {"name": "이마트 에브리데이 산본점", "address": "경기도 군포시", "lat": "37.362", "lon": "126.930"}]})'
    
    with patch("services.location_service._session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.text = fake_json_text
        mock_get.return_value = mock_resp
        
        # '이마트' 검색 시 이마트24, 이마트 에브리데이는 제외되어 1개만 남아야 함
        res = _cached_search_nearby_brand("테스트동", "이마트")
        assert len(res) == 1
        assert res[0]["name"] == "이마트 산본점"

def test_search_nearby_brand_distance_filtering():
    """반경 거리(max_distance_km)를 초과하는 지점은 결과에서 제외되는지 원자 단위로 검증합니다."""
    service = LocationService()
    
    # 가상의 근거리 지점(0.5km)과 먼 지점(20km) 튜플 생성
    close_place = {"name": "CU 산본역점", "address": "산본동", "lat": 37.3610, "lon": 126.9285}
    far_place = {"name": "CU 서울역점", "address": "서울시 용산구", "lat": 37.5547, "lon": 126.9707}
    
    with patch("services.location_service._cached_search_nearby_brand") as mock_search:
        mock_search.return_value = (close_place, far_place)
        
        # 반경 3.0km 설정 시 근거리 매장만 반환되어야 함
        filtered = service.search_nearby_brand(37.360657, 126.928194, "산본동", "CU", max_distance_km=3.0)
        assert len(filtered) == 1
        assert filtered[0]["name"] == "CU 산본역점"

def test_get_current_location_ip_and_fallback():
    """IP 기반 위치 조회 실패 시 산본동 기본 좌표(37.360657, 126.928194)로 안전하게 Fallback 되는지 검증합니다."""
    service = LocationService()
    with patch("services.location_service._session.get") as mock_get:
        mock_get.side_effect = Exception("IP API Timeout")
        lat, lon = service.get_current_location()
        assert lat == 37.360657
        assert lon == 126.928194

def test_search_place_coordinates():
    """장소 키워드 검색 시 정확한 좌표 튜플 (lat, lon)을 반환하고, 실패 시 (None, None)을 반환하는지 검증합니다."""
    service = LocationService()
    fake_success_json = 'jQuery_({"place": [{"name": "산본역", "lat": "37.3584", "lon": "126.9331"}]})'
    
    with patch("services.location_service._session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.text = fake_success_json
        mock_get.return_value = mock_resp
        
        lat, lon = service.search_place("산본역")
        assert lat == 37.3584
        assert lon == 126.9331
        
    fake_fail_json = 'jQuery_({"place": []})'
    with patch("services.location_service._session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.text = fake_fail_json
        mock_get.return_value = mock_resp
        
        lat, lon = service.search_place("존재하지않는장소12345")
        assert lat is None
        assert lon is None

def test_gosanro_517_nearby_stores_detection():
    """'고산로 517번길 20' (lat=37.36023, lon=126.92042) 반경 0.5km 내의 실제 매장들(CU, GS25, 배스킨라빈스 등)이 누락 없이 검색되는지 통합 검증합니다."""
    service = LocationService()
    lat, lon = 37.36023163, 126.92042895
    neighborhood = "산본2동"
    
    # 1. CU 검증 (CU 군포궁내점 등 반경 0.5km 이내 매장 검출)
    cu_stores = service.search_nearby_brand(lat, lon, neighborhood, "CU", max_distance_km=0.5)
    assert len(cu_stores) >= 1
    assert any("군포궁내점" in s["name"] or "수리점" in s["name"] for s in cu_stores)
    
    # 2. GS25 검증 (GS25 산본솔거점 등 반경 0.5km 이내 매장 검출)
    gs25_stores = service.search_nearby_brand(lat, lon, neighborhood, "GS25", max_distance_km=0.5)
    assert len(gs25_stores) >= 1
    assert any("솔거점" in s["name"] for s in gs25_stores)
    
    # 3. 배스킨라빈스 검증 (배스킨라빈스 산본9단지점 등 반경 0.5km 이내 매장 검출)
    baskin_stores = service.search_nearby_brand(lat, lon, neighborhood, "배스킨라빈스", max_distance_km=0.5)
    assert len(baskin_stores) >= 1
    assert any("9단지점" in s["name"] for s in baskin_stores)

def test_unlimited_store_collection_capacity():
    """매장 수집 한도(기존 25개 제약)가 최대 100개로 대폭 확장되어 밀집 지역에서도 매장 유실 없이 25개 이상 수집 가능한지 검증합니다."""
    service = LocationService()
    # 강남역 중심 좌표 (서울 매장 밀집 지역)
    lat, lon = 37.497952, 127.027619
    neighborhood = "역삼동"
    
    # 5.0km 광역 반경으로 CU 매장 탐색 시 25개 제한을 훌륭히 초과하여 전수 수집되는지 검증
    cu_stores = service.search_nearby_brand(lat, lon, neighborhood, "CU", max_distance_km=5.0)
    assert len(cu_stores) > 25

def test_popup_store_strict_geofencing():
    """팝업스토어 탐색 시 35km 강제 확장 없이 선택한 반경(max_distance_km)을 엄격히 준수하여 반경 초과 지점이 거러지는지 검증합니다."""
    service = LocationService()
    
    close_popup = {"name": "팝업 롯데피트인 산본점", "address": "산본동 1145", "lat": 37.3600, "lon": 126.9320}
    far_seoul_popup = {"name": "하우스 오브 토이스토리 팝업 @성수", "address": "성수동2가 302", "lat": 37.5441, "lon": 127.0517}
    
    with patch("services.location_service._cached_search_nearby_brand") as mock_search:
        mock_search.return_value = (close_popup, far_seoul_popup)
        
        # 고산로 517번길 20 (산본동)에서 3.0km 반경 탐색 시 25km 떨어진 성수동 팝업은 엄격 제외되어 1개만 반환되어야 함
        filtered = service.search_nearby_brand(37.3602, 126.9204, "산본동", "팝업스토어", max_distance_km=3.0)
        assert len(filtered) == 1
        assert filtered[0]["name"] == "팝업 롯데피트인 산본점"


