import pytest
from unittest.mock import patch, MagicMock
from main import _run_scrapers, fetch_global_alerts, fetch_local_alerts
from services.scraper_service import AbstractScraper

class MockDummyScraper(AbstractScraper):
    def __init__(self):
        super().__init__("DummyScraper")
        
    def scrape(self):
        return [
            {"target": "CU", "title": "편의점 혜택 타이틀", "details": "http://cu.com", "category": "편의점 혜택"},
            {"target": "알수없는곳", "title": "기타 혜택", "details": "http://unknown.com", "category": "미정의카테고리"}
        ]

def test_run_scrapers_categorization():
    """스크래핑 결과가 사전 정의된 카테고리에 정확히 분류되고, 미정의 카테고리는 '기타'로 안전 이관되는지 검증합니다."""
    scrapers = [MockDummyScraper()]
    res = _run_scrapers(scrapers)
    
    assert "편의점 혜택" in res
    assert len(res["편의점 혜택"]) == 1
    assert res["편의점 혜택"][0]["target"] == "CU"
    
    assert "기타" in res
    assert len(res["기타"]) == 1
    assert res["기타"][0]["target"] == "알수없는곳"

def test_fetch_global_alerts():
    """fetch_global_alerts() 파이프라인 호출 시 하이브리드 스크래퍼 기반 딕셔너리를 반환하는지 검증합니다."""
    with patch("main.HybridOfficialScraper") as mock_hybrid:
        mock_hybrid.return_value.scrape.return_value = [
            {"target": "GS25", "title": "GS 갓세일", "details": "http://gs25.com", "category": "편의점 혜택"}
        ]
        
        alerts = fetch_global_alerts()
        assert "편의점 혜택" in alerts
        assert len(alerts["편의점 혜택"]) == 1

def test_fetch_local_alerts_mapping():
    """사용자 좌표 기반으로 오프라인 카테고리 혜택이 내 주변 매장으로 역매핑되어 '내 주변 매장 혜택' 딕셔너리로 통합되는지 검증합니다."""
    global_results = {
        "편의점 혜택": [
            {"target": "CU", "title": "쓔퍼세일 1+1", "details": "http://cu.com", "category": "편의점 혜택"}
        ]
    }
    
    mock_places = [
        {"name": "CU 산본에듀점", "address": "산본동 100", "road_address": "산본로 123", "lat": 37.361, "lon": 126.928}
    ]
    
    def _search_side_effect(lat, lon, neighborhood, brand, max_distance_km=3.0):
        if brand in ["맛집", "가볼만한 곳"]:
            return []
        return mock_places

    with patch("main.LocationService") as mock_loc_cls:
        mock_instance = MagicMock()
        mock_instance.get_neighborhood.return_value = "산본동"
        mock_instance.search_nearby_brand.side_effect = _search_side_effect
        mock_loc_cls.return_value = mock_instance
        
        local_alerts = fetch_local_alerts(37.360657, 126.928194, global_results, radius_km=3.0)
        
        assert "내 주변 매장 혜택" in local_alerts
        results = local_alerts["내 주변 매장 혜택"]
        assert len(results) == 1
        assert results[0]["brand"] == "CU"
        assert results[0]["target"] == "CU 산본에듀점"
        assert results[0]["title"] == "쓔퍼세일 1+1"
        assert results[0]["category"] == "내 주변 매장 혜택"
