import requests
import json
import urllib.parse

lat, lon = 37.3602, 126.9282 # 고산로 517번길 20 (산본동, 군포시)

headers = {
    'Referer': 'https://map.kakao.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

test_queries = [
    "CU",
    "산본동 CU",
    "산본 CU",
    "군포시 CU",
    "군포 CU",
    "스타벅스",
    "산본동 스타벅스",
    "산본 스타벅스",
    "군포 스타벅스",
    "올리브영",
    "산본 올리브영"
]

print("=== KAKAO MAP WEB API QUERY TEST ===")
for q in test_queries:
    encoded_q = urllib.parse.quote(q)
    url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery_&q={encoded_q}&x={lon}&y={lat}&page=1&msFlag=A&sort=0"
    resp = requests.get(url, headers=headers, timeout=4)
    if resp.status_code == 200:
        text = resp.text
        if '(' in text and ')' in text:
            text = text[text.index('(')+1:text.rindex(')')]
        data = json.loads(text)
        places = data.get('place', [])
        print(f"Query [{q:<18}]: Returned {len(places):<2} places")
        if places:
            for p in places[:2]:
                print(f"    -> {p.get('name')} | {p.get('address')}")
    else:
        print(f"Query [{q}]: HTTP {resp.status_code}")
