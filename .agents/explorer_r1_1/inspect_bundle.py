import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("Total JS length:", len(js))

# Find all .get(...) calls on searchParams/URLSearchParams
param_get_matches = re.findall(r'(\w+)\.get\((["\'])([^"\']+)\2\)', js)
keys = sorted(list(set(k for var, q, k in param_get_matches)))
print("Found searchParam keys:", keys)

# Look for specific keys related to search / query / address / q / location
target_keys = ["q", "search", "query", "address", "addr", "keyword", "loc", "location", "k", "s", "place", "p"]
found_targets = [k for k in keys if k in target_keys]
print("Target search keys found:", found_targets)

# Print code snippets around these target keys
for var, q, k in param_get_matches:
    if k in target_keys or "search" in k.lower() or "query" in k.lower() or "addr" in k.lower():
        pattern = f'{var}.get({q}{k}{q})'
        for m in re.finditer(re.escape(pattern), js):
            pos = m.start()
            snippet = js[max(0, pos-150):min(len(js), pos+250)]
            print(f"\n=== Key: '{k}' at pos {pos} ===")
            print(snippet)
