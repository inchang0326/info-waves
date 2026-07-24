import pytest
from unittest.mock import patch, MagicMock
from services.scraper_service import GuziMapScraper
from services.ui_utils import format_expander_title, get_category_marker_icon, infer_category_from_brand
from main import fetch_local_alerts

def test_guzimap_scraper_data_fetching():
    """거지맵(GuziMap) API에서 초저가/가성비 식당 데이터를 정확히 수집하는지 검증합니다."""
    fake_guzi_data = [
        {
            "id": "test-id-1",
            "name": "짜신 산본본점",
            "address": "경기도 군포시 광정로 68",
            "latest_menu_name": "짜장면",
            "latest_price_krw": 3000,
            "lat": 37.3602,
            "lng": 126.9204,
            "naver_place_id": "https://naver.me/test"
        }
    ]
    
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_guzi_data
        mock_get.return_value = mock_resp
        
        scraper = GuziMapScraper()
        results = scraper.scrape()
        
        assert len(results) == 1
        item = results[0]
        assert item["category"] == "거지맵 (가성비 식당 & 초저가 혜택)"
        assert "짜신 산본본점" in item["target"]
        assert "3,000원" in item["title"]
        assert item["details"] == "https://naver.me/test"
        assert item["lat"] == 37.3602
        assert item["lon"] == 126.9204

def test_guzimap_local_alert_geofencing():
    """거지맵 식당이 사용자 좌표 반경(3.0km) 이내에 있을 경우 정상 노출되고, 초과할 경우 제외되는지 검증합니다."""
    guzi_item_close = {
        "target": "거지맵 - 짜신 산본본점",
        "title": "거지맵 가성비 식당: 짜장면 (3,000원)",
        "details": "https://xn--v69ak0xskm.com",
        "category": "거지맵 (가성비 식당 & 초저가 혜택)",
        "lat": 37.3602,
        "lon": 126.9204, # 0.87km from Sanbon center
        "brand": "짜신 산본본점"
    }
    guzi_item_far = {
        "target": "거지맵 - 꼬숑돈까스",
        "title": "거지맵 가성비 식당: 돈까스 (4,000원)",
        "details": "https://xn--v69ak0xskm.com",
        "category": "거지맵 (가성비 식당 & 초저가 혜택)",
        "lat": 37.5569,
        "lon": 126.9441, # Sinchon (25km away from Sanbon)
        "brand": "꼬숑돈까스"
    }
    
    global_results = {
        "거지맵 (가성비 식당 & 초저가 혜택)": [guzi_item_close, guzi_item_far]
    }
    
    # 산본 고산로 517번길 20 좌표 (37.3602, 126.9204) 3.0km 반경 탐색
    local_data = fetch_local_alerts(37.3602, 126.9204, global_results, radius_km=3.0)
    guzi_local = local_data.get("거지맵 (가성비 식당 & 초저가 혜택)", [])
    
    assert len(guzi_local) == 1
    assert guzi_local[0]["brand"] == "짜신 산본본점"

def test_guzimap_ui_styling_and_formatting():
    """거지맵 카테고리의 Expander Title 포맷팅 및 지도 핀 마커 스타일(darkgreen + cutlery)을 검증합니다."""
    # 1. Expander Title
    title = format_expander_title("거지맵 (가성비 식당 & 초저가 혜택)", 5)
    assert "거지맵 (가성비 식당) (5개)" in title
    
    # 2. Marker Icon & Color
    icon_info = get_category_marker_icon("짜신 산본본점", "거지맵 (가성비 식당 & 초저가 혜택)")
    assert icon_info["color"] == "darkgreen"
    assert icon_info["icon"] == "cutlery"
    assert icon_info["prefix"] == "fa"
    
    # 3. Category Inference
    inferred = infer_category_from_brand("거지맵 - 꼬숑돈까스")
    assert inferred == "거지맵 (가성비 식당 & 초저가 혜택)"
