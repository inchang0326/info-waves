import concurrent.futures
from services.location_service import LocationService
from services.scraper_service import (
    RuliwebHotDealScraper, NaverPlaceDirectScraper,
    HybridOfficialScraper
)
from services.logger_utils import setup_logger

logger = setup_logger(__name__)
def fetch_global_alerts() -> dict:
    logger.info("글로벌(위치 무관) 데이터 스크래핑을 시작합니다...")
    scrapers = [
        HybridOfficialScraper(),
        RuliwebHotDealScraper(),
    ]
    return _run_scrapers(scrapers)
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def fetch_local_alerts(lat: float, lon: float, _global_results: dict, radius_km: float = 3.0) -> dict:
    lat = round(float(lat), 5)
    lon = round(float(lon), 5)
    radius_km = round(float(radius_km), 2)
    logger.info(f"로컬(위치 기반) 데이터 역매핑을 시작합니다 (좌표: {lat}, {lon}, 반경: {radius_km}km)...")
    location_service = LocationService()
    neighborhood = location_service.get_neighborhood(lat, lon)
    
    local_mapped_results = []
    
    # Extract only the keys relevant to offline locations
    offline_categories = [
        "편의점 혜택", "카페 및 베이커리/디저트", "H&B 스토어", 
        "외식/패스트푸드 및 피자/치킨", "대형마트 통합", 
        "여가 및 쇼핑 혜택", "백화점 및 프리미엄 아울렛"
    ]
    
    def _process_item(item):
        brand = item.get("target")
        if not brand: return []
        places = location_service.search_nearby_brand(lat, lon, neighborhood, brand, max_distance_km=radius_km)
        res = []
        for p in places:
            res.append({
                "brand": brand,
                "target": p["name"],
                "title": item.get('title'),
                "details": item.get("details"),
                "category": "내 주변 매장 혜택",
                "address": p["address"],
                "road_address": p.get("road_address", ""),
                "lat": p.get("lat"),
                "lon": p.get("lon")
            })
        return res

    items_to_process = []
    for cat in offline_categories:
        if cat in _global_results:
            items_to_process.extend(_global_results[cat])

    unique_brands = list(set(item.get("target") for item in items_to_process if item.get("target")))

    brand_to_places = {}
    def _fetch_brand(b):
        return b, location_service.search_nearby_brand(lat, lon, neighborhood, b, max_distance_km=radius_km)

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(_fetch_brand, b) for b in unique_brands]
        for future in concurrent.futures.as_completed(futures):
            try:
                b, places = future.result()
                brand_to_places[b] = places
            except Exception as e:
                logger.exception(f"주변 매장 검색 중 오류 발생: {e}")

    for item in items_to_process:
        brand = item.get("target")
        if not brand: continue
        places = brand_to_places.get(brand, [])
        for p in places:
            local_mapped_results.append({
                "brand": brand,
                "target": p["name"],
                "title": item.get('title'),
                "details": item.get("details"),
                "category": "내 주변 매장 혜택",
                "address": p["address"],
                "road_address": p.get("road_address", ""),
                "lat": p.get("lat"),
                "lon": p.get("lon")
            })

    return {"내 주변 매장 혜택": local_mapped_results}
def _run_scrapers(scrapers) -> dict:
    categorized_results = {
        "통신사 멤버십 혜택": [],
        "금융 및 앱테크": [],
        "배달앱 주간 할인": [],
        "편의점 혜택": [],
        "카페 및 베이커리/디저트": [],
        "H&B 스토어": [],
        "외식/패스트푸드 및 피자/치킨": [],
        "대형마트 통합": [],
        "백화점 및 프리미엄 아울렛": [],
        "여가 및 쇼핑 혜택": [],
        "여행 및 숙박": [],
        "핫딜 커뮤니티": [],
        "대형마트 새소식(동네)": [],
        "팝업스토어(동네)": [],
        "기타": []
    }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(scrapers))) as executor:
        future_to_scraper = {executor.submit(scraper.scrape): scraper for scraper in scrapers}
        for future in concurrent.futures.as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                results = future.result()
                for result in results:
                    cat = result.get('category', '기타')
                    if cat not in categorized_results:
                        cat = '기타'
                    categorized_results[cat].append(result)
            except Exception as e:
                logger.exception(f"[{scraper.name}] 실행 중 오류 발생: {e}")
                
    return categorized_results
