import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("=== 1. Searching for all calls to Ir(...) in JS Bundle ===")
for m in re.finditer(r'\bIr\(', js):
    pos = m.start()
    snippet = js[max(0, pos-150):min(len(js), pos+200)].replace('\n', ' ')
    print(f"[{pos}] {snippet}")

print("\n=== 2. Searching for all calls to bn(...) in JS Bundle ===")
for m in re.finditer(r'\bbn\(', js):
    pos = m.start()
    snippet = js[max(0, pos-150):min(len(js), pos+200)].replace('\n', ' ')
    print(f"[{pos}] {snippet}")
