import re

with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = 2603002
print("=== Component state initializers around pos 2603000 to 2607000 ===")
print(js[pos-500:pos+3500])
