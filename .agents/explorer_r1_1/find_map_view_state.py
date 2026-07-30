import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("=== 1. Searching for all functions parsing window.location.search or de ===")
for m in re.finditer(r'new URLSearchParams\((de|window\.location\.search|search|t|e|a\.search)\)', js):
    pos = m.start()
    snippet = js[max(0, pos-150):min(len(js), pos+250)].replace('\n', ' ')
    print(f"[{pos}] {snippet}")
