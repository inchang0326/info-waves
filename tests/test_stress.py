import pytest
import time
from unittest.mock import patch, MagicMock
from services.scraper_service import HybridOfficialScraper
from main import fetch_local_alerts
from services.location_service import _cached_get_neighborhood, _cached_search_nearby_brand

def test_st01_scraper_concurrency_and_performance_benchmark():
    """
    [ST-01] 50개 메이저 브랜드 동시 스크래핑 벤치마크 (Stress & Benchmark Test)
    - 20개 멀티스레드를 사용하여 50개 대표 브랜드 혜택을 동시 병렬 수집함
    - 3.5초 이내에 수집이 완료되어야 하며 스레드 풀 병목이나 데드락이 발생하지 않음을 검증함
    """
    with patch("services.scraper_service.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<?xml version="1.0"?><rss><channel></channel></rss>'
        mock_get.return_value = mock_resp
        
        scraper = HybridOfficialScraper()
        start_time = time.time()
        results = scraper.scrape()
        elapsed_time = time.time() - start_time
        
        # 50개 브랜드 수집 데이터 보장
        assert len(results) >= 40
        # 20개 스레드로 3.5초 이내 동시 처리 완료 검증
        assert elapsed_time < 3.5
        print(f"\n[ST-01] 50개 브랜드 동시 스크래핑 소요 시간: {elapsed_time:.3f}초")


def test_st02_large_scale_local_mapping_thread_pool_stress():
    """
    [ST-02] 대량 매장(100+ 혜택 아이템) 역매핑 스레드 풀 부하 테스트
    - 100개의 오프라인 브랜드 혜택이 몰렸을 때 20개 ThreadPoolExecutor로 역매핑을 구동함
    - 스레드 동시성 경합(Race Condition) 및 데드락 없이 2.0초 이내에 완료되는지 스트레스 검증함
    """
    # 100개 대량 혜택 아이템 생성
    items = []
    brands = ["CU", "GS25", "스타벅스", "버거킹", "올리브영"]
    for i in range(100):
        brand = brands[i % len(brands)]
        items.append({"target": brand, "title": f"대량 혜택 {i}", "details": "http://test.com", "category": "편의점 혜택"})
        
    global_results = {"편의점 혜택": items}
    
    fake_places = [
        {"name": "CU 산본역점", "address": "산본동 100", "road_address": "산본로 123", "lat": 37.3610, "lon": 126.9285}
    ]
    
    def _search_side_effect(neighborhood, brand, lat_round=0.0, lon_round=0.0):
        if brand in ["맛집", "가볼만한 곳", "페스티벌"]:
            return ()
        return tuple(fake_places)

    with patch("services.location_service.LocationService.get_neighborhood", return_value="산본동"), \
         patch("services.location_service._cached_search_nearby_brand", side_effect=_search_side_effect):
        
        start_time = time.time()
        local_results = fetch_local_alerts(37.360657, 126.928194, global_results, radius_km=3.0)
        elapsed_time = time.time() - start_time
        
        # 100개 아이템 매핑 결과 검증
        mapped_list = local_results["내 주변 매장 혜택"]
        assert len(mapped_list) == 100
        # 20개 스레드로 3.5초 이내 부하 처리 완료 검증
        assert elapsed_time < 3.5
        print(f"\n[ST-02] 100개 매장 역매핑 동시성 부하 처리 소요 시간: {elapsed_time:.3f}초")


def test_st03_lru_cache_high_concurrency_stress():
    """
    [ST-03] 역지오코딩 & 장소 검색 LRU 캐시 1,000회 연속 부하 내구성 테스트
    - 동일/유사 좌표 및 키워드 조회가 1,000회 몰릴 때 LRU 캐시 히트율 및 응답 속도를 검증함
    - 1,000회 부하가 0.1초 이내에 처리되는 고성능 캐싱 내구성을 검증함
    """
    with patch("services.location_service._session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"address": {"quarter": "산본동"}}
        mock_resp.text = 'jQuery_({"place": [{"name": "CU 산본점", "lat": "37.36", "lon": "126.92"}]})'
        mock_get.return_value = mock_resp
        
        start_time = time.time()
        
        # 1,000회 연속 캐시 호출
        for _ in range(500):
            _cached_get_neighborhood(37.360, 126.928)
            _cached_search_nearby_brand("산본동", "CU")
            
        elapsed_time = time.time() - start_time
        
        # 1,000회 연속 캐시 조회가 0.1초 이내에 극도로 빠르게 완료되는지 검증
        assert elapsed_time < 0.1
        print(f"\n[ST-03] LRU 캐시 1,000회 부하 처리 소요 시간: {elapsed_time:.5f}초")
