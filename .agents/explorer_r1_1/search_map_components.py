import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("=== Searching for Routes in JS Bundle ===")
routes = re.findall(r'path:["\']([^"\']+)["\']', js)
print("Found path routes:", set(routes))

print("\n=== Searching for search input placeholder / UI in map component ===")
for m in re.finditer(r'placeholder:[^,}]+', js):
    snippet = js[max(0, m.start()-50):min(len(js), m.end()+50)]
    if any(k in snippet for k in ['검색', '식당', '주소', '지역', 'search', 'query']):
        clean_snippet = snippet.replace('\n', ' ')
        print(f"[{m.start()}] {clean_snippet}")
