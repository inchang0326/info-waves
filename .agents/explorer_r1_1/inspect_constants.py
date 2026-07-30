with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = 1055494
print("=== Code around pos 1054000 to 1059000 ===")
print(js[pos-1500:pos+3500])
