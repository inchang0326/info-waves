import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Let's search for '/r/' or '/map' or 'restaurant' route helpers
print("=== 1. Searching for restaurant/map path constants ===")
for m in re.finditer(r'["\']/(r|map|restaurant|place|places)["\']', js):
    pos = m.start()
    snippet = js[max(0, pos-150):min(len(js), pos+200)].replace('\n', ' ')
    print(f"[{pos}] {snippet}")

print("\n=== 2. Searching for URLSearchParams or search handling around map/restaurant ===")
for m in re.finditer(r'searchParams|URLSearchParams|location\.search|\.search\b', js):
    pos = m.start()
    snippet = js[max(0, pos-100):min(len(js), pos+150)].replace('\n', ' ')
    if any(k in snippet for k in ['restaurant', 'place', 'map', 'q', 'search', 'query', 'addr']):
        print(f"[{pos}] {snippet}")
