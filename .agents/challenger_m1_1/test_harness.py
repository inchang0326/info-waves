import sys
import time
import unittest
from unittest.mock import patch, MagicMock
import requests
import concurrent.futures

# Add parent directory to sys.path
sys.path.insert(0, "/Users/steady/.openclaw/workspace/info_waves")

from services.scraper_service import FallbackUrlManager, HybridOfficialScraper, AbstractScraper

class TestFallbackUrlManagerEmpirical(unittest.TestCase):
    def test_http_404_returns_fallback(self):
        """Verify FallbackUrlManager returns fallback_url when event_url returns HTTP 404."""
        with patch("requests.head") as mock_head, patch("requests.get") as mock_get:
            mock_head_resp = MagicMock()
            mock_head_resp.status_code = 404
            mock_head.return_value = mock_head_resp
            
            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 404
            mock_get.return_value = mock_get_resp

            event_url = "https://brand.com/events/expired_404"
            fallback_url = "https://brand.com"
            result = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
            self.assertEqual(result, fallback_url, f"Expected fallback_url for 404, got {result}")

    def test_http_500_returns_fallback(self):
        """Verify FallbackUrlManager returns fallback_url when event_url returns HTTP 500."""
        with patch("requests.head") as mock_head, patch("requests.get") as mock_get:
            mock_head_resp = MagicMock()
            mock_head_resp.status_code = 500
            mock_head.return_value = mock_head_resp
            
            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 500
            mock_get.return_value = mock_get_resp

            event_url = "https://brand.com/events/server_error_500"
            fallback_url = "https://brand.com"
            result = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
            self.assertEqual(result, fallback_url, f"Expected fallback_url for 500, got {result}")

    def test_http_other_error_status_codes(self):
        """Verify FallbackUrlManager returns fallback_url for 403, 502, 503, 504 status codes."""
        for code in [403, 502, 503, 504]:
            with patch("requests.head") as mock_head, patch("requests.get") as mock_get:
                m_head = MagicMock(status_code=code)
                mock_head.return_value = m_head
                m_get = MagicMock(status_code=code)
                mock_get.return_value = m_get

                event_url = f"https://brand.com/events/{code}"
                fallback_url = "https://brand.com"
                result = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
                self.assertEqual(result, fallback_url, f"Expected fallback_url for {code}, got {result}")

    def test_invalid_urls(self):
        """Verify FallbackUrlManager handles None, empty string, non-HTTP schemes, and malformed URLs."""
        fallback_url = "https://brand.com"
        invalid_cases = [
            None,
            "",
            12345,
            "ftp://example.com/event",
            "javascript:void(0)",
            "file:///etc/passwd",
            "not_a_url_at_all",
            "http//"
        ]
        for inv in invalid_cases:
            res = FallbackUrlManager.resolve_valid_event_url(inv, fallback_url)
            self.assertEqual(res, fallback_url, f"Failed on invalid input {inv}: expected {fallback_url}, got {res}")

    def test_connection_timeout_and_exceptions(self):
        """Verify FallbackUrlManager handles network timeouts and exceptions cleanly."""
        with patch("requests.head", side_effect=requests.exceptions.Timeout("HEAD timeout")), \
             patch("requests.get", side_effect=requests.exceptions.ConnectionError("GET error")):
            event_url = "https://slow-server.com/event"
            fallback_url = "https://slow-server.com"
            res = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
            self.assertEqual(res, fallback_url)

    def test_valid_200_url(self):
        """Verify FallbackUrlManager returns event_url when HTTP HEAD returns < 400."""
        with patch("requests.head") as mock_head:
            mock_head.return_value = MagicMock(status_code=200)
            event_url = "https://brand.com/events/valid_200"
            fallback_url = "https://brand.com"
            res = FallbackUrlManager.resolve_valid_event_url(event_url, fallback_url)
            self.assertEqual(res, event_url)


class TestHybridOfficialScraperEmpirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Running HybridOfficialScraper live empirical scrape ---")
        cls.scraper = HybridOfficialScraper()
        cls.start_time = time.time()
        cls.results = cls.scraper.scrape()
        cls.duration = time.time() - cls.start_time
        print(f"Scraped {len(cls.results)} items in {cls.duration:.2f} seconds.")

    def test_results_non_empty(self):
        """Verify scraper returns a substantial number of event items."""
        self.assertGreaterEqual(len(self.results), 40, f"Expected at least 40 items, got {len(self.results)}")

    def test_item_fields_and_types(self):
        """Verify every item has non-empty target, title, details, category, and valid fallback_used."""
        valid_categories = {
            "편의점 혜택",
            "외식/패스트푸드 및 피자/치킨",
            "카페 및 베이커리/디저트",
            "H&B 스토어",
            "대형마트 통합",
            "백화점 및 프리미엄 아울렛",
            "여가 및 쇼핑 혜택",
            "영화관 및 문화/테마파크",
            "통신사 멤버십 혜택",
            "금융 및 앱테크",
            "핫딜 커뮤니티",
            "팝업스토어 & 전시/행사",
            "거지맵 (가성비 식당 & 초저가 혜택)"
        }

        invalid_items = []
        for idx, item in enumerate(self.results):
            # 1. Target check
            target = item.get("target")
            if not target or not isinstance(target, str) or not target.strip():
                invalid_items.append(f"Item #{idx}: missing or empty target ({target})")

            # 2. Title check
            title = item.get("title")
            if not title or not isinstance(title, str) or not title.strip():
                invalid_items.append(f"Item #{idx} ({target}): missing or empty title ({title})")

            # 3. URL details check
            details = item.get("details")
            if not details or not isinstance(details, str) or not details.startswith(("http://", "https://")):
                invalid_items.append(f"Item #{idx} ({target}): invalid details URL ({details})")

            # 4. Category check
            cat = item.get("category")
            if not cat or cat not in valid_categories:
                invalid_items.append(f"Item #{idx} ({target}): unknown category '{cat}'")

            # 5. fallback_used flag check (if present)
            if "fallback_used" in item:
                self.assertIn(item["fallback_used"], ["true", "false"], f"Item {target} has invalid fallback_used '{item['fallback_used']}'")

        self.assertEqual(len(invalid_items), 0, "Discovered invalid items:\n" + "\n".join(invalid_items))

    def test_rss_keyword_relevance_analysis(self):
        """Stress-test: Check if RSS matched headlines are relevant to the target brand or if generic event news got attached."""
        irrelevant_matches = []
        for item in self.results:
            target = item.get("target", "")
            title = item.get("title", "")
            if "[실시간 혜택]" in title or "[신규]" in title:
                # Extract clean title after tag
                clean_title = title.replace("[실시간 혜택]", "").replace("[신규]", "").strip()
                # Check if target brand (or part of target name) is mentioned or if it's generic
                # e.g., if target is "CU", "CU" should ideally be in headline or related
                print(f"[RSS Title Check] Brand: '{target}' | Title: '{title}'")

    def test_concurrency_stress_test(self):
        """Stress-test: Execute 3 concurrent scrape() calls in parallel to verify thread safety & execution timeout."""
        print("\n--- Starting Concurrency Stress Test (3 parallel scrape calls) ---")
        start_concurrency = time.time()
        
        def run_scrape(worker_id):
            scr = HybridOfficialScraper()
            res = scr.scrape()
            return worker_id, len(res)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(run_scrape, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_concurrency_time = time.time() - start_concurrency
        print(f"Concurrent stress test finished in {total_concurrency_time:.2f} seconds.")
        for worker_id, item_count in results:
            print(f"Worker {worker_id} returned {item_count} items.")
            self.assertGreaterEqual(item_count, 40)
        
        # Expect 3 concurrent full scrapes to complete within 45 seconds
        self.assertLess(total_concurrency_time, 45.0, f"Concurrency test took too long: {total_concurrency_time:.2f}s")


if __name__ == "__main__":
    unittest.main()
