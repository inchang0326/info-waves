import pytest
from unittest.mock import patch, MagicMock
from services.scraper_service import (
    AbstractScraper, RuliwebHotDealScraper, HybridOfficialScraper
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
    # 구글 뉴스 RSS 수집부를 mock 처리하여 base_data 정합성만 검증
    with patch.object(HybridOfficialScraper, "_fetch_news_headline", return_value=""):
        scraper = HybridOfficialScraper()
        results = scraper.scrape()
        
        assert len(results) >= 40 # 최소 40개 이상의 메이저 브랜드 보장
        for item in results:
            assert "target" in item and len(item["target"]) > 0
            assert "title" in item and len(item["title"]) > 0
            assert "details" in item and item["details"].startswith(("http://", "https://"))
            assert "category" in item and len(item["category"]) > 0
