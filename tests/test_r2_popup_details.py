import pytest
from unittest.mock import patch, MagicMock
from services.location_service import LocationService
from services.ui_utils import generate_mini_popup_html, generate_card_html
from main import fetch_local_alerts

def test_fetch_popup_event_details_structure():
    """R2-01: Verify fetch_popup_event_details returns non-empty structured event details dictionary."""
    ls = LocationService()
    
    with patch("services.location_service._session.get") as mock_get:
        mock_resp_kakao = MagicMock()
        mock_resp_kakao.status_code = 200
        mock_resp_kakao.json.return_value = {
            "basicInfo": {
                "openHour": {
                    "periodList": [
                        {"timeList": [{"timeSE": "11:00 ~ 20:00"}]}
                    ]
                },
                "tags": ["체험존", "전시", "포토존"],
                "homepage": "https://brand-popup.com",
                "phonenum": "02-1234-5678"
            }
        }
        mock_get.return_value = mock_resp_kakao
        
        details = ls.fetch_popup_event_details(brand="데이지크 팝업", confirmid="123456", address="성수동2가")
        
        assert "description" in details and details["description"]
        assert "event_status" in details and details["event_status"] == "🔥 진행중"
        assert "schedule" in details and "11:00 ~ 20:00" in details["schedule"]
        assert "event_content" in details and "체험존" in details["event_content"]
        assert "source_url" in details and details["source_url"] == "https://brand-popup.com"


def test_fetch_local_alerts_attaches_popup_details():
    """R2-02: Verify fetch_local_alerts attaches R2 event detail fields to popup store items."""
    global_results = {
        "팝업스토어 & 전시/행사": [
            {"target": "팝플리 (POPPLY)", "title": "팝업스토어", "details": "https://popply.co.kr", "category": "팝업스토어 & 전시/행사"}
        ]
    }
    fake_places = [
        {"name": "데이지크 성수 팝업스토어", "address": "서울 성동구 성수동2가 301", "road_address": "아차산로 10", "lat": 37.5441, "lon": 127.0543, "confirmid": "999"}
    ]

    def _search_side_effect(neighborhood, brand, lat_round=0.0, lon_round=0.0):
        if brand in ["맛집", "가볼만한 곳"]:
            return ()
        return tuple(fake_places)

    with patch.object(LocationService, "get_neighborhood", return_value="성수동2가"), \
         patch("services.location_service._cached_search_nearby_brand", side_effect=_search_side_effect), \
         patch.object(LocationService, "fetch_popup_event_details") as mock_details:
        
        mock_details.return_value = {
            "description": "💡 데이지크 첫 대형 성수동 팝업스토어 오픈",
            "event_status": "🔥 진행중",
            "schedule": "영업시간 11:00 ~ 20:00",
            "event_content": "전시, 체험존, 굿즈 증정",
            "source_url": "https://news.daum.net/event1"
        }

        local_results = fetch_local_alerts(37.5441, 127.0543, global_results, radius_km=3.0)
        popups = local_results.get("팝업스토어 & 전시/행사", [])

        assert len(popups) >= 1
        item = popups[0]
        assert item["brand"] == "데이지크 성수 팝업스토어"
        assert item["description"] == "💡 데이지크 첫 대형 성수동 팝업스토어 오픈"
        assert item["event_status"] == "🔥 진행중"
        assert item["schedule"] == "영업시간 11:00 ~ 20:00"
        assert item["event_content"] == "전시, 체험존, 굿즈 증정"
        assert item["source_url"] == "https://news.daum.net/event1"


def test_generate_mini_popup_html_with_details():
    """R2-03: Verify generate_mini_popup_html renders popup details, status badge, schedule, and links."""
    item_dict = {
        "description": "📰 데이지크 성수 팝업스토어",
        "event_status": "🔥 진행중",
        "schedule": "매일 11:00 ~ 20:00",
        "source_url": "https://event-news.com"
    }

    popup_html = generate_mini_popup_html(
        brand="데이지크 팝업",
        title="[데이지크 팝업] 성수동 - 실시간 팝업",
        link="https://map.naver.com",
        item_dict=item_dict
    )

    assert "데이지크 팝업" in popup_html
    assert "📰 데이지크 성수 팝업스토어" in popup_html
    assert "자세히 보기" in popup_html


def test_generate_card_html_with_popup_details():
    """R2-04: Verify generate_card_html renders event details box with description, schedule, and status badge."""
    branches = [
        {
            "target": "데이지크 성수 팝업스토어",
            "address": "서울 성동구 성수동2가 301",
            "road_address": "성수아차산로 10",
            "description": "✨ 데이지크 뷰티 팝업 및 브랜드 체험존",
            "event_status": "🔥 진행중",
            "schedule": "영업시간 11:00 ~ 20:00",
            "event_content": "전시, 포토존, 굿즈 증정",
            "source_url": "https://daesique-popup.com"
        }
    ]

    card_html = generate_card_html(
        brand="데이지크 팝업",
        title="[데이지크 팝업] 성수동 팝업스토어",
        link="https://map.naver.com",
        branches=branches
    )

    assert "✨ 데이지크 뷰티 팝업 및 브랜드 체험존" in card_html
    assert "전시, 포토존, 굿즈 증정" in card_html


def test_popup_detail_fallback_on_network_error():
    """R2-05: Verify popup detail fetching returns structured fallback on network failure."""
    ls = LocationService()
    
    with patch("services.location_service._session.get", side_effect=Exception("Network Offline")):
        details = ls.fetch_popup_event_details(brand="테스트 팝업", confirmid="err_id", address="서울")
        
        assert details["event_status"] == "🔥 진행중"
        assert "테스트 팝업" in details["description"]
        assert "영업시간" in details["schedule"] or "매장" in details["schedule"]
        assert details["source_url"] == ""
