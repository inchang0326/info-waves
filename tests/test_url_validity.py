import pytest
import requests
from services.scraper_service import HybridOfficialScraper

def test_all_brand_urls_non_404():
    """
    Scraper의 모든 브랜드별 URL이 HTTP 404 오류를 발생시키지 않는지 검증합니다.
    (HTTP 200, 301, 302, 403 WAF 등 허용하되 404 혜택 페이지 오류 없음 검증)
    """
    scraper = HybridOfficialScraper()
    items = scraper.scrape()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    broken_404_urls = []
    for item in items:
        target = item.get("target")
        url = item.get("details")
        assert url is not None, f"Brand {target} has no detail URL"
        
        try:
            res = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            if res.status_code >= 400:
                res = requests.get(url, headers=headers, timeout=5, stream=True)
            if res.status_code == 404:
                broken_404_urls.append((target, url))
        except Exception:
            # Connection timeouts or WAF blocks are handled, but 404 explicitly fails
            pass

    assert len(broken_404_urls) == 0, f"Found 404 error URLs: {broken_404_urls}"
