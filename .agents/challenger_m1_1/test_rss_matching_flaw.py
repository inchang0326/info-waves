import sys
import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

sys.path.insert(0, "/Users/steady/.openclaw/workspace/info_waves")
from services.scraper_service import HybridOfficialScraper, FallbackUrlManager

class TestRssMatchingFlaw(unittest.TestCase):
    def test_rss_irrelevant_brand_pollution(self):
        """
        Empirically verify if _fetch_realtime_brand_event attaches an irrelevant news headline
        about a different brand (e.g. Starbucks) to a target brand (e.g. 천년닭강정)
        because the RSS title contains generic keywords ('할인', '이벤트').
        """
        # Google RSS search for "천년닭강정" returns an article about Starbucks discount
        fake_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>스타벅스, 서머 음료 50% 할인 이벤트 진행 - 중앙일보</title>
                    <link>https://news.naver.com/read?id=123</link>
                    <description>스타벅스코리아가 오늘부터 파격 할인행사를 시작합니다.</description>
                </item>
            </channel>
        </rss>
        """
        with patch("services.scraper_service.requests.get") as mock_get, \
             patch.object(FallbackUrlManager, "resolve_valid_event_url", return_value="https://1000dak.co.kr"):
            
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = fake_rss
            mock_get.return_value = mock_resp
            
            scraper = HybridOfficialScraper()
            item_config = {
                "target": "천년닭강정",
                "title": "패밀리 사이즈 포장 할인 & 배달 리뷰 이벤트",
                "details": "https://1000dak.co.kr",
                "fallback_url": "https://1000dak.co.kr",
                "category": "외식/패스트푸드 및 피자/치킨"
            }
            
            result = scraper._fetch_realtime_brand_event(item_config)
            
            print("\n--- Empirical RSS Matching Test Output ---")
            print("Target Brand:", result["target"])
            print("Returned Title:", result["title"])
            
            # If the title contains "스타벅스" for target "천년닭강정", that's a cross-brand pollution flaw!
            is_polluted = "스타벅스" in result["title"] and "천년닭강정" not in result["title"]
            print(f"Is title polluted with irrelevant brand news? {is_polluted}")
            
            self.assertTrue(is_polluted, "Flaw demonstrated: generic keyword match caused Starbucks news to be attached to 천년닭강정")

    def test_fallback_url_manager_invalid_fallback(self):
        """
        Empirically verify FallbackUrlManager behavior when both event_url AND fallback_url are invalid/broken or fallback_url is empty.
        """
        res = FallbackUrlManager.resolve_valid_event_url("https://broken.invalid/event", None)
        print("\n--- FallbackUrlManager with None fallback_url ---")
        print("Result:", res)
        self.assertIsNone(res, "When fallback_url is None, resolve_valid_event_url returns None")

if __name__ == "__main__":
    unittest.main()
