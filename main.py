import math
import urllib.parse
import concurrent.futures
import re
import streamlit as st

from services.location_service import LocationService
from services.scraper_service import (
    RuliwebHotDealScraper, NaverPlaceDirectScraper,
    HybridOfficialScraper
)
from services.logger_utils import setup_logger

logger = setup_logger(__name__)

@st.cache_data(ttl=60 * 60, show_spinner=False)
def fetch_global_alerts() -> dict:
    logger.info("글로벌(위치 무관) 데이터 스크래핑을 시작합니다...")
    scrapers = [
        HybridOfficialScraper(),
    ]
    return _run_scrapers(scrapers)


@st.cache_data(ttl=60, show_spinner=False)
def fetch_local_alerts(lat: float, lon: float, _global_results: dict, radius_km: float = 3.0, _cache_ver: int = 2) -> dict:
    lat = round(float(lat), 5)
    lon = round(float(lon), 5)
    radius_km = round(float(radius_km), 2)
    logger.info(f"로컬(위치 기반) 데이터 역매핑을 시작합니다 (좌표: {lat}, {lon}, 반경: {radius_km}km)...")
    
    location_service = LocationService()
    neighborhood = location_service.get_neighborhood(lat, lon)
    
    local_categorized_results = {
        "주변 가볼만한 곳": [],
        "주변 추천 맛집": [],
        "거지맵 (가성비 식당 & 초저가 혜택)": [],
        "팝업스토어 & 전시/행사": [],
        "카페 및 베이커리/디저트": [],
        "백화점 및 프리미엄 아울렛": [],
        "영화관 및 문화/테마파크": [],
        "대형마트 통합": [],
        "여가 및 쇼핑 혜택": [],
        "H&B 스토어": [],
        "편의점 혜택": [],
        "외식/패스트푸드 및 피자/치킨": [],
    }
    
    all_local_items = []

    # =========================================================================
    # 1. 거지맵 Bounding Box 정밀 필터링
    # =========================================================================
    guzi_global = _global_results.get("거지맵 (가성비 식당 & 초저가 혜택)", [])
    guzi_with_dist = []
    
    lat_margin = radius_km / 111.0
    current_lat_rad = math.radians(lat)
    lon_degree_len = 111.0 * math.cos(current_lat_rad)
    lon_margin = radius_km / lon_degree_len

    for item in guzi_global:
        i_lat = item.get("lat")
        i_lon = item.get("lon")
        if i_lat is not None and i_lon is not None:
            # 1차 필터링: Bounding Box 밖의 식당은 삼각함수 계산 없이 즉시 버림
            if not (lat - lat_margin <= i_lat <= lat + lat_margin and 
                    lon - lon_margin <= i_lon <= lon + lon_margin):
                continue
            
            # 2차 필터링: 박스 안의 후보들만 정확한 구면 거리 계산
            dist = location_service._calculate_distance(lat, lon, i_lat, i_lon)
            if dist <= radius_km:
                mapped_item = dict(item)
                mapped_item["distance_km"] = round(dist, 2)
                mapped_item["target"] = item.get("brand", item.get("target"))
                mapped_item["orig_category"] = "거지맵 (가성비 식당 & 초저가 혜택)"
                guzi_with_dist.append((dist, mapped_item))

    # 지정 반경 이내 매장 정렬 (가까운 순)
    guzi_with_dist.sort(key=lambda x: x[0])

    for dist_val, item_copy in guzi_with_dist:
        raw_title = item_copy.get("title", "")
        clean_title = re.sub(r"^📍\s*\[[\d\.]+km\]\s*", "", raw_title)
        item_copy["title"] = f"📍 [{dist_val}km] {clean_title}"
        local_categorized_results["거지맵 (가성비 식당 & 초저가 혜택)"].append(item_copy)
        
        local_item = dict(item_copy)
        local_item["category"] = "내 주변 매장 혜택"
        all_local_items.append(local_item)
    
    # =========================================================================
    # 2. 브랜드 핫딜 매장 검색 로직
    # =========================================================================
    for cat in list(local_categorized_results.keys()):
        if cat in ["거지맵 (가성비 식당 & 초저가 혜택)", "주변 추천 맛집", "주변 가볼만한 곳"]:
            continue
        items_in_cat = _global_results.get(cat, [])
        if not items_in_cat: continue
        
        unique_brands = list(set(item.get("target") for item in items_in_cat if item.get("target")))
        
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

        seen_popup_coords = set()
        for item in items_in_cat:
            brand = item.get("target")
            if not brand: continue
            places = brand_to_places.get(brand, [])
            for p in places:
                event_details = {}
                if cat == "팝업스토어 & 전시/행사":
                    coord_key = (round(p["lat"], 4), round(p["lon"], 4), p["name"])
                    if coord_key in seen_popup_coords:
                        continue
                    seen_popup_coords.add(coord_key)
                    actual_brand = p["name"]
                    actual_title = f"[{p['name']}] {p.get('address', '')} - 팝업스토어 & 브랜드 행사진행 현황"
                    actual_details = item.get("source_url") or item.get("details")

                    event_details = location_service.fetch_popup_event_details(
                        brand=p["name"],
                        confirmid=p.get("confirmid"),
                        address=p.get("address", "")
                    )
                else:
                    actual_brand = brand
                    actual_title = item.get("title")
                    actual_details = item.get("source_url") or item.get("details")

                mapped_item = {
                    "brand": actual_brand,
                    "target": p["name"],
                    "title": actual_title,
                    "details": actual_details,
                    "category": cat,
                    "orig_category": cat,
                    "address": p["address"],
                    "road_address": p.get("road_address", ""),
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                    "description": event_details.get("description", item.get("description", "")),
                    "event_status": event_details.get("event_status", "🔥 진행중"),
                    "schedule": event_details.get("schedule", ""),
                    "event_content": event_details.get("event_content", ""),
                    "source_url": event_details.get("source_url") or actual_details
                }
                local_categorized_results[cat].append(mapped_item)
                
                local_item = dict(mapped_item)
                local_item["category"] = "내 주변 매장 혜택"
                all_local_items.append(local_item)

    # =========================================================================
    # 3. 주변 맛집, 가볼만한 곳 병렬 다이렉트 조회
    # =========================================================================
    keywords_to_search = {
        "주변 추천 맛집": "맛집",
        "주변 가볼만한 곳": "가볼만한 곳"
    }

    def _fetch_keyword_places(cat_name, keyword):
        places = location_service.search_nearby_brand(lat, lon, neighborhood, keyword, max_distance_km=radius_km)
        return cat_name, places

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as kw_executor:
        kw_futures = [kw_executor.submit(_fetch_keyword_places, cat, kw) for cat, kw in keywords_to_search.items()]
        
        for future in concurrent.futures.as_completed(kw_futures):
            try:
                cat_name, places = future.result()
                
                for p in places[:20]: # 상위 20개만 노출
                    dist_km = round(p.get("distance_km", 0.0), 2)
                    encoded_name = urllib.parse.quote(p["name"])
                    naver_url = f"https://search.naver.com/search.naver?query={encoded_name}"
                    
                    mapped_item = {
                        "brand": p["name"],
                        "target": p["name"],
                        "title": f"📍 [{dist_km}km] {p.get('address', '')}",
                        "details": naver_url,
                        "category": cat_name,
                        "orig_category": cat_name,
                        "address": p.get("address", ""),
                        "lat": p.get("lat"),
                        "lon": p.get("lon")
                    }
                    
                    local_categorized_results[cat_name].append(mapped_item)
                    
                    local_item = dict(mapped_item)
                    local_item["category"] = "내 주변 매장 혜택"
                    all_local_items.append(local_item)
                    
            except Exception as e:
                logger.exception(f"주변 {cat_name} 검색 중 오류 발생: {e}")

    # 최종 결과 병합
    local_categorized_results["내 주변 매장 혜택"] = all_local_items
    return local_categorized_results


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
        "영화관 및 문화/테마파크": [],
        "여행 및 숙박": [],
        "핫딜 커뮤니티": [],
        "팝업스토어 & 전시/행사": [],
        "거지맵 (가성비 식당 & 초저가 혜택)": [],
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
