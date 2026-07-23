import requests
import json
import math
import re
import functools
from typing import Tuple, List, Dict
from requests.adapters import HTTPAdapter
from services.logger_utils import setup_logger

import urllib.parse
from config import settings

logger = setup_logger(__name__)

# Shared requests Session with HTTP connection pooling for fast parallel network requests
_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=40, pool_maxsize=40)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

@functools.lru_cache(maxsize=256)
def _cached_get_neighborhood(lat_round: float, lon_round: float) -> str:
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "ko"
    }
    params = {
        "lat": lat_round,
        "lon": lon_round,
        "format": "json",
        "zoom": 14
    }
    try:
        resp = _session.get(url, headers=headers, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})
        neighborhood = address.get('quarter') or address.get('suburb') or address.get('city_district') or address.get('borough') or address.get('town') or address.get('city', '서울')
        logger.info(f"OpenStreetMap Reverse Geocoding: {lat_round}, {lon_round} -> {neighborhood}")
        return neighborhood
    except Exception as e:
        logger.exception(f"Failed to reverse geocode: {e}")
        return "여의도동"

import os
import sqlite3

class PersistentLocationCache:
    def __init__(self, db_path: str = "data/location_cache.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS location_cache (
                        cache_key TEXT PRIMARY KEY,
                        json_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to initialize SQLite location cache: {e}")

    def get(self, cache_key: str) -> Tuple[Dict[str, str], ...]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT json_data FROM location_cache WHERE cache_key = ?", (cache_key,))
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    return tuple(data)
        except Exception as e:
            logger.warning(f"SQLite cache get error: {e}")
        return None

    def put(self, cache_key: str, data: List[Dict[str, str]]):
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO location_cache (cache_key, json_data) VALUES (?, ?)",
                    (cache_key, json.dumps(data, ensure_ascii=False))
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"SQLite cache put error: {e}")

_disk_cache = PersistentLocationCache()

@functools.lru_cache(maxsize=1024)
def _cached_search_nearby_brand(neighborhood: str, brand: str, lat_round: float = 0.0, lon_round: float = 0.0) -> Tuple[Dict[str, str], ...]:
    cache_key = f"{neighborhood}:{brand}:{lat_round}:{lon_round}"
    cached_res = _disk_cache.get(cache_key)
    if cached_res is not None:
        return cached_res
    queries = []
    if neighborhood:
        queries.append(f"{neighborhood} {brand}")
        base_dong = re.sub(r"\d+동$", "동", neighborhood)
        if base_dong and base_dong != neighborhood:
            queries.append(f"{base_dong} {brand}")
        short_name = re.sub(r"동$", "", base_dong)
        if short_name and short_name != base_dong:
            queries.append(f"{short_name} {brand}")
    queries.append(brand)

    headers = {
        'Referer': 'https://map.kakao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    seen = set()
    results = []
    for q in queries:
        encoded_q = urllib.parse.quote(q)
        url1 = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&x={lon_round}&y={lat_round}&page=1&msFlag=A&sort=0" if (lat_round and lon_round) else f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&page=1&msFlag=A&sort=0"
        try:
            resp = _session.get(url1, headers=headers, timeout=4)
            text = resp.text
            if '(' in text and ')' in text:
                text = text[text.index('(')+1:text.rindex(')')]
            data = json.loads(text)
            places = data.get('place', [])
            if not places:
                continue
            
            for p in places:
                p_lat, p_lon = p.get("lat"), p.get("lon")
                p_name = p.get("name", "")
                
                if brand == "이마트" and ("24" in p_name or "에브리데이" in p_name): continue
                if brand == "GS25" and "수퍼" in p_name: continue
                
                key = p.get("confirmid") or f"{p_name}_{p_lat}_{p_lon}"
                if key not in seen and p_lat and p_lon:
                    seen.add(key)
                    results.append({
                        "name": p_name,
                        "address": p.get("address", ""),
                        "road_address": p.get("new_address", ""),
                        "lat": float(p_lat),
                        "lon": float(p_lon)
                    })
                    if len(results) >= 100: break
            
            # If page 1 had 15 results, fetch pages 2 and 3 for full coverage
            if len(places) >= 15 and len(results) < 100:
                for page in (2, 3):
                    url_p = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&x={lon_round}&y={lat_round}&page={page}&msFlag=A&sort=0" if (lat_round and lon_round) else f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&page={page}&msFlag=A&sort=0"
                    resp_p = _session.get(url_p, headers=headers, timeout=4)
                    text_p = resp_p.text
                    if '(' in text_p and ')' in text_p:
                        text_p = text_p[text_p.index('(')+1:text_p.rindex(')')]
                    data_p = json.loads(text_p)
                    places_p = data_p.get('place', [])
                    if not places_p: break
                    for p in places_p:
                        p_lat, p_lon = p.get("lat"), p.get("lon")
                        p_name = p.get("name", "")
                        if brand == "이마트" and ("24" in p_name or "에브리데이" in p_name): continue
                        if brand == "GS25" and "수퍼" in p_name: continue
                        key = p.get("confirmid") or f"{p_name}_{p_lat}_{p_lon}"
                        if key not in seen and p_lat and p_lon:
                            seen.add(key)
                            results.append({
                                "name": p_name,
                                "address": p.get("address", ""),
                                "road_address": p.get("new_address", ""),
                                "lat": float(p_lat),
                                "lon": float(p_lon)
                            })
                            if len(results) >= 100: break
                    if len(results) >= 100: break

            # SMART EARLY EXIT: Stop redundant query fallbacks if neighborhood stores were found
            if len(results) > 0:
                break

        except Exception as e:
            logger.exception(f"Failed to search Kakao Maps for {brand}: {e}")
            
        if len(results) >= 100:
            break
            
    _disk_cache.put(cache_key, results)
    return tuple(results)

class LocationService:
    def get_current_location(self) -> Tuple[float, float]:
        """
        Fetches the current latitude and longitude based on the machine's IP address.
        """
        try:
            resp = _session.get("http://ip-api.com/json/", timeout=5)
            data = resp.json()
            if data.get("status") == "success":
                lat = data["lat"]
                lon = data["lon"]
                logger.info(f"📍 IP-based Location: {lat}, {lon}")
                return float(lat), float(lon)
        except Exception as e:
            logger.warning(f"Failed to fetch IP-based location (Timeout/Network): {e}")
        
        return 37.360657, 126.928194

    def get_neighborhood(self, lat: float, lon: float) -> str:
        return _cached_get_neighborhood(round(lat, 3), round(lon, 3))

    def search_nearby_brand(self, lat: float, lon: float, neighborhood: str, brand: str, max_distance_km: float = 5.0) -> List[Dict[str, str]]:
        lat_r = round(lat, 3)
        lon_r = round(lon, 3)
        places = _cached_search_nearby_brand(neighborhood, brand, lat_r, lon_r)
        filtered = []
        for p in places:
            dist = self._calculate_distance(lat, lon, p["lat"], p["lon"])
            if dist <= max_distance_km:
                p_copy = dict(p)
                p_copy["distance_km"] = dist
                filtered.append(p_copy)
        filtered.sort(key=lambda x: x["distance_km"])
        return filtered

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0 # Earth radius in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def search_place(self, keyword: str) -> Tuple[float, float]:
        if not keyword or not keyword.strip():
            return None, None
            
        clean_kw = keyword.strip()
        encoded_kw = urllib.parse.quote(clean_kw)

        # Tier 1: Official Kakao REST API (If KAKAO_API_KEY is configured in settings or environment)
        kakao_key = getattr(settings, 'kakao_api_key', None) or os.getenv('KAKAO_API_KEY')
        if kakao_key:
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            for endpoint in ["keyword", "address"]:
                url = f"https://dapi.kakao.com/v2/local/search/{endpoint}.json?query={encoded_kw}"
                try:
                    resp = _session.get(url, headers=headers, timeout=4)
                    if resp.status_code == 200:
                        docs = resp.json().get("documents", [])
                        if docs:
                            lat = docs[0].get("y") or docs[0].get("lat")
                            lon = docs[0].get("x") or docs[0].get("lng")
                            if lat and lon:
                                logger.info(f"Kakao REST API Search Success for '{clean_kw}': {lat}, {lon}")
                                return float(lat), float(lon)
                except Exception as e:
                    logger.warning(f"Kakao REST API ({endpoint}) failed for '{clean_kw}': {e}")

        # Tier 2: Kakao Web Search (with URL encoding)
        url_kakao_web = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_kw}&msFlag=A&sort=0"
        headers_kakao_web = {
            'Referer': 'https://map.kakao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            resp = _session.get(url_kakao_web, headers=headers_kakao_web, timeout=4)
            text = resp.text
            if '(' in text and ')' in text:
                text = text[text.index('(')+1:text.rindex(')')]
            data = json.loads(text)
            places = data.get('place', [])
            for p in places:
                p_lat = p.get("lat")
                p_lon = p.get("lon")
                if p_lat and p_lon:
                    logger.info(f"Kakao Web Search Success for '{clean_kw}': {p_lat}, {p_lon}")
                    return float(p_lat), float(p_lon)
        except Exception as e:
            logger.warning(f"Kakao Web Search failed for '{clean_kw}': {e}")

        # Tier 3: OpenStreetMap Nominatim Geocoding Fallback (Works globally & on Streamlit Cloud without IP blocking)
        url_nom = f"https://nominatim.openstreetmap.org/search?q={encoded_kw}&format=json&countrycodes=kr"
        headers_nom = {
            'User-Agent': 'InfoWavesApp/1.0 (https://infowaves.streamlit.app)'
        }
        try:
            resp = _session.get(url_nom, headers=headers_nom, timeout=4)
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    lat = results[0].get("lat")
                    lon = results[0].get("lon")
                    if lat and lon:
                        logger.info(f"OpenStreetMap Nominatim Search Success for '{clean_kw}': {lat}, {lon}")
                        return float(lat), float(lon)
        except Exception as e:
            logger.warning(f"Nominatim Search failed for '{clean_kw}': {e}")

        return None, None

