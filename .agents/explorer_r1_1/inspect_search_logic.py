import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("=== 1. Literal Query Parameter Patterns ===")
query_patterns = [
    r'["\']\?q=["\']', r'["\']\?search=["\']', r'["\']\?query=["\']', r'["\']\?address=["\']', r'["\']\?keyword=["\']',
    r'\bq\b', r'\bsearch\b', r'\bquery\b', r'\baddress\b', r'\bkeyword\b'
]

# Let's search for useSearchParams or location.search or window.location
print("\n=== 2. location / search occurrences ===")
for m in re.finditer(r'(\w+)\.search', js):
    pos = m.start()
    var_name = m.group(1)
    if var_name in ['location', 'loc', 'url', 'window', 'req', 'parsed']:
        snippet = js[max(0, pos-100):min(len(js), pos+150)]
        print(f"Match: {var_name}.search at pos {pos}:")
        print("  ", snippet.replace('\n', ' '))

print("\n=== 3. Search input placeholders & search state ===")
placeholder_matches = [m.start() for m in re.finditer(r'placeholder:\s*["\'][^"\']*검색[^"\']*["\']', js)]
for pos in placeholder_matches:
    snippet = js[max(0, pos-200):min(len(js), pos+300)]
    print(f"Placeholder match at pos {pos}:")
    print(snippet)

print("\n=== 4. Search function definitions / state setters ===")
for m in re.finditer(r'setSearch|setQuery|setKeyword|searchQuery|searchKeyword', js):
    pos = m.start()
    snippet = js[max(0, pos-100):min(len(js), pos+200)]
    print(f"State match at pos {pos}:")
    print(snippet.replace('\n', ' '))
