import sys
sys.path.insert(0, '.')

from services.ui_utils import get_brand_logo

test_brands = [
    "할리스", "천년닭강정", "60계치킨", "동대문엽기떡볶이", "한솥도시락",
    "신전떡볶이", "역전할머니맥주", "GS더프레시", "무인양품", "롯데월드",
    "CU", "GS25", "스타벅스", "맥도날드", "버거킹", "올리브영", "다이소"
]

print("=== BRAND LOGO TEST ===")
for b in test_brands:
    logo = get_brand_logo(b)
    is_base64_svg = logo.startswith("data:image/svg+xml;base64,")
    is_google_favicon = "google.com/s2/favicons" in logo
    print(f"Brand [{b:<12}]: {'SVG Base64 (OK)' if is_base64_svg else ('Google Favicon' if is_google_favicon else 'Other')} -> {logo[:60]}...")
