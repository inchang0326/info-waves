import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = 2655000
print("=== Searching for R_ definition ===")
for m in re.finditer(r'\bR_\s*=', js):
    p = m.start()
    if 2600000 <= p <= 2700000:
        print(f"[{p}] {js[max(0, p-200):min(len(js), p+400)]}")

print("=== Searching for Jt state definition ===")
for m in re.finditer(r'\[Jt,\s*hT\]', js):
    p = m.start()
    print(f"[{p}] {js[max(0, p-200):min(len(js), p+400)]}")
