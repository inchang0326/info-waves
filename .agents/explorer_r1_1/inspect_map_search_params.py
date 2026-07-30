with open('/Users/steady/.openclaw/workspace/info_waves/.agents/explorer_r1_1/guzimap_bundle.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = 2680891
print("=== Code around pos 2676000 to 2682000 ===")
print(js[pos-4000:pos+1500])
