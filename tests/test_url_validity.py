import pytest
import requests
import concurrent.futures
from services.scraper_service import HybridOfficialScraper

def test_all_brand_urls_non_404():
    """
    Scraper의 모든 브랜드별 URL이 HTTP 404 및 500 오류를 발생시키지 않는지 병렬(ThreadPool) 검증합니다.
    """
    scraper = HybridOfficialScraper()
    items = scraper.scrape()
    
    desktop_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    
    def check_url(item):
        target = item.get("target")
        url = item.get("details")
        if not url:
            return target, url, "No URL"
        
        errors = []
        for ua in [desktop_ua, mobile_ua]:
            try:
                res = requests.get(url, headers={'User-Agent': ua}, timeout=4, stream=True)
                if res.status_code in (404, 500):
                    errors.append((res.status_code, ua))
            except Exception:
                pass
        if errors:
            return target, url, errors
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_url, items))

    broken_urls = [r for r in results if r is not None]
    assert len(broken_urls) == 0, f"Found 404/500 error URLs: {broken_urls}"

