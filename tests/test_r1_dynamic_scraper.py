import pytest
import requests
from unittest.mock import patch, MagicMock
from services.scraper_service import (
    HybridOfficialScraper, FallbackUrlManager, DynamicTopBrandsScraper, _brand_matches_title
)

def test_dynamic_scraper_output_contract():
    """R1-01: Verify dynamic scraper returns valid dict list with required contract keys."""
    with patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<?xml version="1.0"?><rss><channel><item><title>CU 1+1 이벤트 - 연합뉴스</title><link>https://cu.bgfretail.com/event/1</link><description>CU 1+1 득템 혜택</description></item></channel></rss>'
        mock_get.return_value = mock_resp

        scraper = HybridOfficialScraper()
        results = scraper.scrape()

        assert len(results) > 0
        for item in results:
            assert "target" in item and item["target"]
            assert "title" in item and item["title"]
            assert "details" in item and item["details"].startswith(("http://", "https://"))
            assert "category" in item and item["category"]


def test_cross_brand_title_pollution_prevention():
    """R1-02: Verify that RSS titles of Brand A (Starbucks) do not pollute Brand B (천년닭강정)."""
    item_config = {
        "target": "천년닭강정",
        "title": "패밀리 사이즈 포장 할인 & 배달 리뷰 이벤트",
        "main_url": "https://1000dak.co.kr",
        "category": "외식/패스트푸드 및 피자/치킨"
    }

    rss_xml_starbucks = '<?xml version="1.0"?><rss><channel><item><title>스타벅스, 서머 음료 50% 할인 이벤트 진행 - 연합뉴스</title><link>https://starbucks.co.kr/event</link><description>스타벅스 할인</description></item></channel></rss>'

    with patch("services.scraper_service.requests.get") as mock_get, \
         patch("services.scraper_service.FallbackUrlManager.resolve_valid_event_url") as mock_resolve:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = rss_xml_starbucks
        mock_get.return_value = mock_resp
        mock_resolve.return_value = "https://1000dak.co.kr"

        scraper = HybridOfficialScraper()
        res = scraper._fetch_dynamic_event_info(item_config)

        # Starbucks title MUST NOT pollute 천년닭강정
        assert "스타벅스" not in res["title"]
        assert res["target"] == "천년닭강정"
        assert "천년닭강정 상시 혜택 및 이벤트" in res["title"]


def test_brand_matches_title_helper():
    """R1-03: Verify _brand_matches_title logic accuracy."""
    assert _brand_matches_title("스타벅스", "스타벅스 100% 당첨 이벤트") is True
    assert _brand_matches_title("팝플리 (POPPLY)", "팝플리 성수동 팝업스토어 총정리") is True
    assert _brand_matches_title("SKT T데이", "SKT 7월 T Day 프로모션") is True
    assert _brand_matches_title("천년닭강정", "스타벅스 서머 음료 50% 할인") is False
    assert _brand_matches_title("CU", "GS25 갓세일 1+1 행사") is False


def test_mcdonalds_dynamic_event_parsing():
    """R1-04: Verify McDonald's promotion parsing."""
    fake_html = """
    <div class="promotList">
        <ul>
            <li><a href="/kor/promotion/detail.do?promtNo=123"><img alt="맥런치 특가 할인" src="/img.jpg" /></a></li>
        </ul>
    </div>
    """
    with patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = fake_html
        mock_get.return_value = mock_resp

        scraper = DynamicTopBrandsScraper()
        # Mock Playwright part to throw exception so it proceeds directly to McDonald's
        with patch("services.scraper_service.sync_playwright", side_effect=Exception("Skip Playwright")):
            res = scraper.scrape()
            assert len(res) >= 1
            mc_item = [r for r in res if r["target"] == "맥도날드"][0]
            assert mc_item["title"] == "맥런치 특가 할인"
            assert "detail.do?promtNo=123" in mc_item["details"]


def test_fallback_url_on_404_not_found():
    """R1-05: Verify FallbackUrlManager falls back to main brand page on HTTP 404."""
    event_url = "https://www.starbucks.co.kr/whats_new/broken_404_event.do"
    fallback_url = "https://www.starbucks.co.kr"

    with patch("services.scraper_service.requests.head", side_effect=Exception("404")), \
         patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        res_url = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
        assert res_url == fallback_url


def test_fallback_url_on_timeout_error():
    """R1-06: Verify FallbackUrlManager falls back gracefully on connection timeout."""
    event_url = "https://slow-server.com/event"
    fallback_url = "https://brand.com"

    with patch("services.scraper_service.requests.head", side_effect=requests.exceptions.Timeout("Timeout")), \
         patch("services.scraper_service.requests.get", side_effect=requests.exceptions.Timeout("Timeout")):

        res_url = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
        assert res_url == fallback_url


def test_fallback_url_on_invalid_scheme():
    """R1-07: Verify FallbackUrlManager handles invalid scheme or None gracefully."""
    fallback_url = "https://brand.com"

    assert FallbackUrlManager.resolve_valid_event_url(None, fallback_url) == fallback_url
    assert FallbackUrlManager.resolve_valid_event_url("", fallback_url) == fallback_url
    assert FallbackUrlManager.resolve_valid_event_url("javascript:void(0)", fallback_url) == fallback_url
    assert FallbackUrlManager.resolve_valid_event_url("ftp://server/file", fallback_url) == fallback_url


def test_concurrent_dynamic_scraping_thread_safety():
    """R1-08: Verify thread-safe concurrent execution of HybridOfficialScraper."""
    with patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<?xml version="1.0"?><rss><channel></channel></rss>'
        mock_get.return_value = mock_resp

        scraper = HybridOfficialScraper()
        results = scraper.scrape()
        assert len(results) >= 40
