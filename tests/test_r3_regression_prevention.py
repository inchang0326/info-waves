import pytest
from unittest.mock import patch, MagicMock
from main import _run_scrapers
from services.scraper_service import AbstractScraper
from services.location_service import PersistentLocationCache
from services.ui_utils import get_category_marker_icon, infer_category_from_brand

class FailingScraper(AbstractScraper):
    def __init__(self):
        super().__init__("FailingScraper")
    def scrape(self):
        raise RuntimeError("Simulated scraper crash")

class WorkingScraper(AbstractScraper):
    def __init__(self):
        super().__init__("WorkingScraper")
    def scrape(self):
        return [{"target": "스타벅스", "title": "별다방 혜택", "details": "https://starbucks.co.kr", "category": "카페 및 베이커리/디저트"}]

def test_all_16_categories_schema_integrity():
    """R3-01: Verify main pipeline initializes and returns all predefined category keys."""
    res = _run_scrapers([])
    expected_categories = [
        "통신사 멤버십 혜택", "금융 및 앱테크", "배달앱 주간 할인", "편의점 혜택",
        "카페 및 베이커리/디저트", "H&B 스토어", "외식/패스트푸드 및 피자/치킨",
        "대형마트 통합", "백화점 및 프리미엄 아울렛", "여가 및 쇼핑 혜택",
        "영화관 및 문화/테마파크", "여행 및 숙박", "핫딜 커뮤니티",
        "팝업스토어 & 전시/행사", "거지맵 (가성비 식당 & 초저가 혜택)", "기타"
    ]
    for cat in expected_categories:
        assert cat in res, f"Category '{cat}' missing from pipeline output"
        assert isinstance(res[cat], list)


def test_main_pipeline_error_isolation():
    """R3-02: Verify single scraper crash does not break the entire pipeline execution."""
    scrapers = [FailingScraper(), WorkingScraper()]
    res = _run_scrapers(scrapers)

    assert "카페 및 베이커리/디저트" in res
    assert len(res["카페 및 베이커리/디저트"]) == 1
    assert res["카페 및 베이커리/디저트"][0]["target"] == "스타벅스"


def test_cache_integrity_with_dynamic_results(tmp_path):
    """R3-03: Verify PersistentLocationCache SQLite storage and retrieval integrity."""
    db_file = str(tmp_path / "test_cache.sqlite")
    cache = PersistentLocationCache(db_path=db_file)

    test_data = [
        {"name": "CU 산본점", "address": "산본동 100", "road_address": "산본로 12", "lat": 37.361, "lon": 126.928}
    ]

    cache.put("v4:산본동:CU:37.361:126.928", test_data)
    cached_res = cache.get("v4:산본동:CU:37.361:126.928")

    assert cached_res is not None
    assert len(cached_res) == 1
    assert cached_res[0]["name"] == "CU 산본점"


def test_category_marker_icon_fallback_safety():
    """R3-04: Verify get_category_marker_icon returns safe, valid icon dict for all categories."""
    categories = [
        "팝업스토어 & 전시/행사", "거지맵 (가성비 식당 & 초저가 혜택)",
        "편의점 혜택", "카페 및 베이커리/디저트", "백화점 및 프리미엄 아울렛",
        "알 수 없는 미정의 카테고리"
    ]

    for cat in categories:
        icon_info = get_category_marker_icon("테스트브랜드", cat)
        assert isinstance(icon_info, dict)
        assert "color" in icon_info
        assert "icon" in icon_info
        assert "prefix" in icon_info
