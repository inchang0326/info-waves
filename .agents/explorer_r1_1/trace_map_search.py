with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = 2660327
print("=== Code around pos 2655000 to 2662000 ===")
print(js[pos-2000:pos+1500])
