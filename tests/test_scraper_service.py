import pytest
from unittest.mock import patch, MagicMock
from services.scraper_service import (
    AbstractScraper, RuliwebHotDealScraper, HybridOfficialScraper, FallbackUrlManager
)

def test_abstract_scraper_raises_not_implemented():
    """AbstractScraper 하위 클래스에서 scrape()를 구현하지 않으면 NotImplementedError가 발생하는지 검증합니다."""
    scraper = AbstractScraper("TestScraper")
    with pytest.raises(NotImplementedError):
        scraper.scrape()

def test_ruliweb_hotdeal_scraper_structure():
    """루리웹 핫딜 스크래퍼가 데이터 구조(target, title, details, category)를 정확히 준수하는지 원자 단위로 검증합니다."""
    fake_html = """
    <html>
        <body>
            <a class="deco" href="https://bbs.ruliweb.com/market/board/1020/read/12345"> [할인] 최신 핫딜 상품 특가 </a>
        </body>
    </html>
    """
    with patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = fake_html
        mock_get.return_value = mock_resp
        
        scraper = RuliwebHotDealScraper()
        results = scraper.scrape()
        
        assert len(results) == 1
        item = results[0]
        assert item["target"] == "루리웹"
        assert item["title"] == "[할인] 최신 핫딜 상품 특가"
        assert item["details"] == "https://bbs.ruliweb.com/market/board/1020/read/12345"
        assert item["category"] == "핫딜 커뮤니티"

def test_hybrid_official_scraper_base_data_integrity():
    """하이브리드 공식 스크래퍼의 50여 개 대표 브랜드 base_data 무결성 및 카테고리 유효성을 검증합니다."""
    # 동적 수집이 느리므로 mock 처리하여 base_data 정합성만 검증
    with patch("services.scraper_service.requests.get") as mock_get, \
         patch("services.scraper_service.GuziMapScraper.scrape", return_value=[]):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<?xml version="1.0"?><rss><channel></channel></rss>'
        mock_get.return_value = mock_resp
        
        scraper = HybridOfficialScraper()
        results = scraper.scrape()
        
        assert len(results) >= 40 # 최소 40개 이상의 메이저 브랜드 보장
        for item in results:
            assert "target" in item and len(item["target"]) > 0
            assert "title" in item and len(item["title"]) > 0
            assert "details" in item and item["details"].startswith(("http://", "https://"))
            assert "category" in item and len(item["category"]) > 0

def test_fallback_url_manager_valid_url():
    """FallbackUrlManager가 유효한 이벤트 URL(HTTP < 400)을 그대로 반환하는지 검증합니다."""
    with patch("services.scraper_service.requests.head") as mock_head:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_head.return_value = mock_resp
        
        event_url = "https://www.starbucks.co.kr/whats_new/campaign_view.do?pro_seq=123"
        fallback_url = "https://www.starbucks.co.kr"
        
        resolved = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
        assert resolved == event_url

def test_fallback_url_manager_404_fallback():
    """FallbackUrlManager가 404, 500 또는 오류 발생 시 브랜드 메인 Landing URL로 자동 Fallback하는지 검증합니다."""
    with patch("services.scraper_service.requests.head") as mock_head, \
         patch("services.scraper_service.requests.get") as mock_get:
        
        mock_head_resp = MagicMock()
        mock_head_resp.status_code = 404
        mock_head.return_value = mock_head_resp
        
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 404
        mock_get.return_value = mock_get_resp
        
        broken_event_url = "https://cu.bgfretail.com/event/broken_page.do"
        main_fallback_url = "https://cu.bgfretail.com"
        
        resolved = FallbackUrlManager.resolve_valid_event_url(broken_event_url, main_fallback_url)
        assert resolved == main_fallback_url

def test_hybrid_official_scraper_dynamic_realtime_rss():
    """HybridOfficialScraper가 RSS 및 실시간 수집을 통해 동적 실시간 이벤트 제목 및 URL을 정상 추출하는지 검증합니다."""
    fake_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>CU, 7월 쓔퍼세일 1+1 행사 이벤트 대규모 진행 - 뉴스통신</title>
                <link>https://cu.bgfretail.com/event/realtime_item.do</link>
                <description>CU에서 7월 한 달간 1+1 득템 행사를 진행합니다.</description>
            </item>
        </channel>
    </rss>
    """
    with patch("services.scraper_service.requests.get") as mock_get, \
         patch.object(FallbackUrlManager, "resolve_valid_event_url", return_value="https://cu.bgfretail.com/event/realtime_item.do"):
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = fake_rss
        mock_get.return_value = mock_resp
        
        scraper = HybridOfficialScraper()
        item_config = {
            "target": "CU",
            "main_url": "https://cu.bgfretail.com",
            "category": "편의점 혜택"
        }
        res = scraper._fetch_dynamic_event_info(item_config)
        
        assert "CU" in res["target"]
        assert "[실시간 혜택]" in res["title"]
        assert "CU, 7월 쓔퍼세일 1+1 행사 이벤트" in res["title"]
        assert res["details"] == "https://cu.bgfretail.com/event/realtime_item.do"
        assert res["category"] == "편의점 혜택"
        assert "1+1 득템 행사" in res.get("description", "")

