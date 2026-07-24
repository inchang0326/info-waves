import urllib.parse
import re
from services.ui_utils import get_brand_logo

brands = ["할리스", "천년닭강정", "60계치킨", "동대문엽기떡볶이", "한솥도시락", "신전떡볶이", "역전할머니맥주", "GS더프레시", "무인양품", "롯데월드"]

for b in brands:
    logo = get_brand_logo(b)
    print(f"{b}: {logo[:50]}...")
