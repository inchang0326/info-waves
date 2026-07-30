import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Let's search for any occurrence of '.get(' in JS bundle to see all parameter names read from URLSearchParams or Map or URL!
param_gets = re.finditer(r'([a-zA-Z0-9_$]+)\.get\(["\']([^"\'\n]+)["\']\)', js)
print("=== All .get('key') calls in entire bundle ===")
results = []
for m in param_gets:
    var_name = m.group(1)
    key = m.group(2)
    pos = m.start()
    results.append((pos, var_name, key))

print(f"Total .get() calls: {len(results)}")
for pos, var_name, key in results:
    snippet = js[max(0, pos-100):min(len(js), pos+150)].replace('\n', ' ')
    print(f"[{pos}] {var_name}.get('{key}'): {snippet}")

