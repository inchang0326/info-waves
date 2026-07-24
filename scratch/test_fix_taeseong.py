import sys
import requests
import json
import math

lat, lon = 37.3876, 127.2435 # 태성로 107
radius_km = 3.0

def calc_dist(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

headers = {'Referer': 'https://map.kakao.com/', 'User-Agent': 'Mozilla/5.0'}

brands = [
    "CU", "GS25", "세븐일레븐", "이마트24",
    "버거킹", "롯데리아", "맘스터치", "KFC", "맥도날드",
    "도미노피자", "피자헛", "노모어피자",
    "교촌치킨", "BBQ", "BHC", "굽네치킨", "60계치킨", "천년닭강정",
    "파리바게뜨", "뚜레쥬르", "배스킨라빈스",
    "스타벅스", "메가커피", "컴포즈커피", "빽다방", "이디야커피", "투썸플레이스", "할리스",
    "올리브영", "다이소", "이마트", "GS더프레시", "동대문엽기떡볶이", "한솥도시락", "신전떡볶이", "역전할머니맥주"
]

print("=== NEW LOGIC TEST: Querying 'brand' centered at (x, y) ===")
total_stores_3km = 0
for b in brands:
    encoded_q = requests.utils.quote(b)
    url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&x={lon}&y={lat}&page=1&msFlag=A&sort=0"
    resp = requests.get(url, headers=headers)
    text = resp.text
    if '(' in text and ')' in text: text = text[text.index('(')+1:text.rindex(')')]
    data = json.loads(text)
    places = data.get('place', [])
    
    count_3km = 0
    for p in places:
        if p.get('lat') and p.get('lon'):
            d = calc_dist(lat, lon, float(p['lat']), float(p['lon']))
            if d <= radius_km:
                count_3km += 1
    total_stores_3km += count_3km
    print(f"Brand [{b:<12}]: Found {count_3km} stores within {radius_km}km")

print(f"\nTOTAL STORES FOUND WITHIN {radius_km}KM FOR 태성로 107: {total_stores_3km}")
