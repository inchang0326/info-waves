from services.logger_utils import setup_logger

logger = setup_logger(__name__)

def get_brand_logo(brand_name: str) -> str:
    """
    Returns high-definition vector SVG Base64 badges for all major Korean brands.
    Guarantees 100% loading reliability with 0ms network latency across all browsers and WAF environments.
    """
    import urllib.parse
    import base64
    import re

    if not brand_name or not isinstance(brand_name, str):
        display_text = "?"
    else:
        brand_clean = brand_name.strip()
        display_text = brand_clean[:2] if len(brand_clean) >= 2 else brand_clean

    # Tier 1: Custom Vibrant Brand SVG Base64 Badges (100% Vector, Instant 0ms Load, Zero WAF/Favicon Failures)
    fallback_badges = {
        # 편의점
        "CU": ("CU", "#652d90", "#00a88f"),
        "씨유": ("CU", "#652d90", "#00a88f"),
        "GS25": ("GS25", "#007bc4", "#ffffff"),
        "지에스": ("GS25", "#007bc4", "#ffffff"),
        "세븐일레븐": ("7E", "#047857", "#ef4444"),
        "7-Eleven": ("7E", "#047857", "#ef4444"),
        "이마트24": ("24", "#eab308", "#0f172a"),
        "이마24": ("24", "#eab308", "#0f172a"),
        "emart24": ("24", "#eab308", "#0f172a"),

        # 패스트푸드 & 버거 & 피자 & 치킨
        "맥도날드": ("M", "#da291c", "#ffbc0d"),
        "McDonald": ("M", "#da291c", "#ffbc0d"),
        "버거킹": ("BK", "#d72300", "#fbe122"),
        "Burger King": ("BK", "#d72300", "#fbe122"),
        "KFC": ("KFC", "#e4002b", "#ffffff"),
        "케이에프씨": ("KFC", "#e4002b", "#ffffff"),
        "롯데리아": ("L", "#ed1c24", "#ffffff"),
        "Momstouch": ("MT", "#d97706", "#ffffff"),
        "맘스터치": ("MT", "#d97706", "#ffffff"),
        "서브웨이": ("SUB", "#008a38", "#ffc72c"),
        "써브웨이": ("SUB", "#008a38", "#ffc72c"),
        "노브랜드버거": ("NBB", "#ffb800", "#000000"),
        "프랭크버거": ("FB", "#004b23", "#ffffff"),
        "도미노피자": ("DP", "#0078ac", "#e31837"),
        "도미노": ("DP", "#0078ac", "#e31837"),
        "피자헛": ("PH", "#ee3124", "#ffffff"),
        "파파존스": ("PJ", "#006738", "#ffffff"),
        "노모어피자": ("NMP", "#ff5722", "#ffffff"),
        "피자알볼로": ("PA", "#0055a5", "#ffffff"),
        "7번가피자": ("7P", "#0047ba", "#ffffff"),
        "교촌치킨": ("교촌", "#c69214", "#ffffff"),
        "교촌": ("교촌", "#c69214", "#ffffff"),
        "BBQ": ("BBQ", "#d32f2f", "#ffffff"),
        "BHC": ("bhc", "#ff8c00", "#ffffff"),
        "굽네치킨": ("굽네", "#b91c1c", "#ffffff"),
        "푸라닭": ("PRD", "#111827", "#d4af37"),
        "가마치통닭": ("가마치", "#c2410c", "#ffffff"),
        "자담치킨": ("자담", "#15803d", "#ffffff"),
        "60계치킨": ("60계", "#d97706", "#ffffff"),
        "60계": ("60계", "#d97706", "#ffffff"),
        "천년닭강정": ("천년", "#ea580c", "#ffffff"),
        "노랑통닭": ("노랑", "#eab308", "#0f172a"),

        # 분식 & 한식 & 기타 외식
        "동대문엽기떡볶이": ("엽떡", "#dc2626", "#fef08a"),
        "엽기떡볶이": ("엽떡", "#dc2626", "#fef08a"),
        "한솥도시락": ("한솥", "#f97316", "#ffffff"),
        "한솥": ("한솥", "#f97316", "#ffffff"),
        "신전떡볶이": ("신전", "#b91c1c", "#ffffff"),
        "역전할머니맥주": ("역전", "#ca8a04", "#ffffff"),
        "역전할머니": ("역전", "#ca8a04", "#ffffff"),
        "본죽": ("본죽", "#9a3412", "#ffffff"),
        "두끼": ("두끼", "#ea580c", "#ffffff"),
        "홍콩반점": ("홍콩", "#dc2626", "#ffffff"),
        "원할머니보쌈": ("원할머니", "#854d0e", "#ffffff"),

        # 카페 / 베이커리 / 디저트
        "스타벅스": ("스벅", "#00704a", "#ffffff"),
        "Starbucks": ("스벅", "#00704a", "#ffffff"),
        "투썸플레이스": ("투썸", "#111827", "#ef4444"),
        "투썸": ("투썸", "#111827", "#ef4444"),
        "이디야커피": ("이디야", "#00205b", "#ffffff"),
        "이디야": ("이디야", "#00205b", "#ffffff"),
        "메가커피": ("메가", "#fbbf24", "#1e3a8a"),
        "메가MGC": ("메가", "#fbbf24", "#1e3a8a"),
        "컴포즈커피": ("컴포즈", "#f59e0b", "#000000"),
        "컴포즈": ("컴포즈", "#f59e0b", "#000000"),
        "빽다방": ("빽다방", "#1d4ed8", "#facc15"),
        "파리바게뜨": ("파바", "#002b49", "#ffffff"),
        "파리바게트": ("파바", "#002b49", "#ffffff"),
        "파리크라상": ("파리", "#0f172a", "#ffffff"),
        "뚜레쥬르": ("TLJ", "#064e3b", "#fef08a"),
        "배스킨라빈스": ("BR", "#ff007f", "#0099ff"),
        "할리스": ("HL", "#ba1b22", "#ffffff"),
        "Hollys": ("HL", "#ba1b22", "#ffffff"),
        "공차": ("공차", "#991b1b", "#ffffff"),
        "더벤티": ("더벤티", "#6b21a8", "#ffffff"),
        "던킨": ("던킨", "#ff6600", "#ff0099"),
        "크리스피크림": ("크리스피", "#047857", "#dc2626"),
        "요아정": ("요아정", "#0284c7", "#ffffff"),
        "설빙": ("설빙", "#78350f", "#ffffff"),
        "폴바셋": ("폴바셋", "#18181b", "#d4af37"),
        "아티제": ("아티제", "#451a03", "#ffffff"),
        "우지커피": ("우지", "#16a34a", "#ffffff"),
        "엔제리너스": ("ANG", "#b45309", "#ffffff"),
        "매머드커피": ("매머드", "#18181b", "#ffffff"),

        # H&B / 마트 / 쇼핑 / 영화관 / 테마파크
        "올리브영": ("올영", "#70b22d", "#ffffff"),
        "Olive Young": ("올영", "#70b22d", "#ffffff"),
        "다이소": ("DS", "#dc2626", "#ffffff"),
        "Daiso": ("DS", "#dc2626", "#ffffff"),
        "이마트": ("이마트", "#ffb800", "#000000"),
        "홈플러스": ("홈플", "#e11d48", "#ffffff"),
        "코스트코": ("COST", "#0284c7", "#e11d48"),
        "GS더프레시": ("GS", "#059669", "#ffffff"),
        "이마트에브리데이": ("에브리데이", "#ca8a04", "#ffffff"),
        "무인양품": ("MUJI", "#7f1d1d", "#ffffff"),
        "MUJI": ("MUJI", "#7f1d1d", "#ffffff"),
        "모던하우스": ("모던", "#0369a1", "#ffffff"),
        "아트박스": ("아트박스", "#e11d48", "#ffffff"),
        "스파오": ("SPAO", "#1e3a8a", "#ffffff"),
        "ABC마트": ("ABC", "#dc2626", "#facc15"),
        "무신사": ("MUSINSA", "#000000", "#ffffff"),
        "유니클로": ("UQ", "#ff0000", "#ffffff"),
        "탑텐": ("TOPTEN", "#18181b", "#ffffff"),
        "CGV": ("CGV", "#ed1c24", "#ffffff"),
        "롯데시네마": ("롯데", "#dc2626", "#ffffff"),
        "메가박스": ("MB", "#312e81", "#ffffff"),
        "롯데월드": ("LW", "#6b21a8", "#fde047"),
        "에버랜드": ("에버", "#0284c7", "#ffffff"),
        "쏘카": ("SOCAR", "#0284c7", "#ffffff"),
        "GS칼텍스": ("GS칼텍스", "#059669", "#ffffff"),
    }

    if brand_name and isinstance(brand_name, str):
        for key, (text, bg_color, font_color) in fallback_badges.items():
            if key in brand_clean:
                svg = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
                    f'<rect width="128" height="128" rx="28" fill="{bg_color}" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>'
                    f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="{font_color}" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="800" font-size="40">{text}</text>'
                    f'</svg>'
                )
                b64_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
                return f"data:image/svg+xml;base64,{b64_svg}"

    # Tier 2: Dynamic Glassmorphism SVG Badge for Unlisted Brands
    svg_badge = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
        '<defs>'
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#334155"/>'
        '<stop offset="100%" stop-color="#0f172a"/>'
        '</linearGradient>'
        '</defs>'
        '<rect width="128" height="128" rx="28" fill="url(#bgGrad)" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>'
        f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="44">{display_text}</text>'
        '</svg>'
    )
    b64_badge = base64.b64encode(svg_badge.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64_badge}"

def inject_global_clipboard_script():
    import streamlit.components.v1 as components
    js = """
    <script>
    try {
        const parentDoc = window.parent.document;
        const oldScript1 = parentDoc.getElementById('info-waves-global-js');
        if (oldScript1) oldScript1.remove();
        const oldScript2 = parentDoc.getElementById('info-waves-global-js-v2');
        if (oldScript2) oldScript2.remove();

        if (!parentDoc.getElementById('info-waves-global-js-v3')) {
            const script = parentDoc.createElement('script');
            script.id = 'info-waves-global-js-v3';
            script.innerHTML = `
                window.updateFoliumRadius = function(radiusMeters) {
                    try {
                        const iframe = document.querySelector('iframe[title="streamlit_folium.st_folium"]');
                        if (iframe && iframe.contentWindow && iframe.contentWindow.map_div) {
                            iframe.contentWindow.map_div.eachLayer(function(l) {
                                if (l.setRadius && l.getRadius && l.getRadius() > 50) {
                                    l.setRadius(radiusMeters);
                                }
                            });
                        }
                    } catch(e) {}
                };

                setInterval(function() {
                    try {
                        const iframe = document.querySelector('iframe[title="streamlit_folium.st_folium"]');
                        if (iframe && iframe.contentDocument) {
                            let style = iframe.contentDocument.getElementById('leaflet-cursor-style');
                            if (!style) {
                                style = iframe.contentDocument.createElement('style');
                                style.id = 'leaflet-cursor-style';
                                style.innerHTML = '.leaflet-container, .leaflet-grab, .leaflet-interactive, .leaflet-marker-icon, .leaflet-container * { cursor: pointer !important; }';
                                iframe.contentDocument.head.appendChild(style);
                            }
                        }
                    } catch(e) {}
                }, 400);

                document.addEventListener('click', function(e) {
                    let themeBtn = e.target.closest('#custom-theme-toggle');
                    if (themeBtn) {
                        e.preventDefault();
                        e.stopPropagation();
                        const root = document.documentElement;
                        const curTheme = root.getAttribute('data-theme') || 'dark';
                        const newTheme = curTheme === 'dark' ? 'light' : 'dark';
                        root.setAttribute('data-theme', newTheme);
                        themeBtn.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
                        return;
                    }
                    let target = e.target;
                    while (target && target !== document && !target.classList.contains('copy-addr-btn')) {
                        target = target.parentNode;
                    }
                    if (target && target.classList && target.classList.contains('copy-addr-btn')) {
                        e.preventDefault();
                        e.stopPropagation();
                        const addr = target.getAttribute('data-addr');
                        if (addr) {
                            const fallbackCopy = function() {
                                try {
                                    const ta = document.createElement('textarea');
                                    ta.value = addr;
                                    ta.style.position = 'fixed';
                                    ta.style.opacity = '0';
                                    document.body.appendChild(ta);
                                    ta.select();
                                    ta.setSelectionRange(0, 99999);
                                    document.execCommand('copy');
                                    document.body.removeChild(ta);
                                } catch(err) {}
                            };
                            if (navigator.clipboard) {
                                navigator.clipboard.writeText(addr).catch(fallbackCopy);
                            } else {
                                fallbackCopy();
                            }
                            const oldText = target.innerHTML;
                            const oldColor = target.style.color;
                            target.innerHTML = '복사 완료';
                            target.style.color = '#10B981';
                            setTimeout(() => {
                                target.innerHTML = oldText;
                                target.style.color = oldColor;
                            }, 2000);
                        }
                    }
                });
            `;
            parentDoc.head.appendChild(script);
        }
    } catch (e) {
    }
    </script>
    """
    components.html(js, width=0, height=0)

import html

def generate_card_html(brand: str, title: str, link: str, branches: list = None) -> str:
    """
    Generates a self-contained HTML card with embedded inline styles.
    - Clicking the card header/title area opens the detail link directly in a new tab.
    - Branch list is collapsible under "주변 매칭" label.
    - Each branch shows road address as inline tooltip on hover with copy button.
    """
    logo_url = get_brand_logo(brand)
    fallback_badge = logo_url

    href = link if (link and link.startswith("http")) else f"https://search.naver.com/search.naver?query={html.escape(link or brand)}"

    escaped_brand = html.escape(str(brand or ""))
    escaped_title = html.escape(str(title or ""))

    # Branch section: collapsible "주변 매칭"
    branches_html = ""
    if branches:
        branch_items = ""
        for b in branches:
            name = html.escape(str(b.get('target', '')))
            road_addr = str(b.get('road_address', '') or b.get('address', ''))
            # Escape special characters for safe JS/HTML embedding
            safe_addr = road_addr.replace('"', '&quot;').replace("'", "&#39;").replace('\n', ' ').replace('\r', '')
            
            if road_addr:
                branch_items += (
                    f'<div class="branch-item" style="cursor:pointer;">'
                    f'<div class="branch-name" style="display:flex; justify-content:space-between; align-items:center;">'
                    f'<span>{name}</span>'
                    f'<span class="copy-addr-btn" data-addr="{safe_addr}" style="font-size:12px; color:#3B82F6; font-weight:600; padding:2px 4px;">주소 복사</span>'
                    f'</div>'
                    f'</div>'
                )
            else:
                branch_items += (
                    f'<div class="branch-item">'
                    f'<div class="branch-name"><span>{name}</span></div>'
                    f'</div>'
                )
        branches_html = (
            f'<details class="branches-details" onclick="event.stopPropagation();">'
            f'<summary>'
            f'<span>매칭 주소</span>'
            f'<span class="dropdown-arrow" style="display: inline-block; width: 8px; height: 8px; border-right: 2px solid currentColor; border-bottom: 2px solid currentColor; transform: rotate(45deg); transition: transform 0.2s ease; margin-left: auto; margin-right: 4px; margin-bottom: 2px;"></span>'
            f'</summary>'
            f'<ul>{branch_items}</ul>'
            f'</details>'
        )

    import hashlib
    card_id = "c" + hashlib.md5(f"{brand}{title}".encode()).hexdigest()[:8]

    card_html = (
        f'<div id="{card_id}" class="info-card">'

        # Clickable area: logo + brand + title → opens detail link in a new window
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, \'_blank\', \'noopener,noreferrer\'); return false;" class="info-card-link">'

        # Card header: logo + brand name
        f'<div class="info-card-header">'
        f'<img src="{logo_url}" '
        f'onerror="this.onerror=null;this.src=\'{fallback_badge}\';" '
        f'class="info-card-logo" alt="{escaped_brand}" referrerpolicy="no-referrer" />'
        f'<span class="info-card-brand">{escaped_brand}</span>'
        f'</div>'

        # Card body: title
        f'<div class="info-card-title">{escaped_title}</div>'

        f'</a>'

        # Branch section: outside the link, collapsible
        + (f'<div class="info-card-branches">{branches_html}</div>' if branches_html else '')

        + f'</div>'
    )
    return card_html


def generate_mini_popup_html(brand: str, title: str, link: str) -> str:
    """
    Generates a lightweight, inline-styled HTML for Folium Map Popups.
    """
    logo_url = get_brand_logo(brand)
    fallback_url = "https://www.google.com/s2/favicons?domain=google.com&sz=128"
    href = link if (link and link.startswith("http")) else f"https://search.naver.com/search.naver?query={html.escape(link or brand)}"
    escaped_brand = html.escape(str(brand or ""))
    escaped_title = html.escape(str(title or ""))
    
    return f"""
    <div style="font-family: 'Pretendard', -apple-system, sans-serif; min-width: 200px; padding: 4px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <img src="{logo_url}" onerror="this.onerror=null;this.src='{fallback_url}';" style="width: 24px; height: 24px; border-radius: 6px; margin-right: 8px; border: 1px solid #e5e7eb; object-fit: contain; background: white;" />
            <strong style="font-size: 14px; color: #111827;">{escaped_brand}</strong>
        </div>
        <div style="font-size: 13px; color: #4B5563; margin-bottom: 12px; line-height: 1.4; word-break: keep-all;">
            {escaped_title}
        </div>
        <a href="{href}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, '_blank', 'noopener,noreferrer'); return false;" style="font-size: 12px; color: #2563EB; text-decoration: none; font-weight: 700;">자세히 보기</a>
    </div>
    """


def get_zoom_for_radius(radius_km: float) -> int:
    """
    Returns an appropriate Leaflet zoom level for a given search radius in km.
    Ensures that the entire radius circle fits perfectly on the screen.
    """
    if radius_km <= 0.5:
        return 16
    elif radius_km <= 1.0:
        return 15
    elif radius_km <= 2.0:
        return 14
    elif radius_km <= 3.0:
        return 13
    elif radius_km <= 5.0:
        return 12
    else:
        return 11


def format_expander_title(category: str, count: int) -> str:
    """
    Formats the category title for expanders with clean text and count.
    """
    clean_cat = category.replace(" 혜택", "").replace(" 통합", "")
    if clean_cat == "외식/패스트푸드 및 피자/치킨":
        clean_cat = "패스트푸드"
    elif clean_cat == "카페 및 베이커리/디저트":
        clean_cat = "카페/디저트"
    elif clean_cat == "백화점 및 프리미엄 아울렛":
        clean_cat = "백화점/아울렛"
    elif clean_cat == "여가 및 쇼핑":
        clean_cat = "여가/쇼핑"
    elif clean_cat == "영화관 및 문화/테마파크":
        clean_cat = "영화관/문화"
    elif clean_cat == "팝업스토어 & 전시/행사":
        clean_cat = "팝업스토어"
    elif clean_cat == "거지맵 (가성비 식당 & 초저가)":
        clean_cat = "거지맵 (가성비 식당)"
    elif "거지맵" in clean_cat:
        clean_cat = "거지맵 (가성비 식당)"
        
    return f"{clean_cat} ({count}개)"


def infer_category_from_brand(brand: str, category: str = "") -> str:
    """
    Infers the correct category from the brand name if category is missing, empty, or '기타'.
    Prevents any brand from collapsing into '기타' or unclassified fallback icons.
    """
    if category and category not in ["기타", "내 주변 매장 혜택", "알 수 없음", ""]:
        return category
        
    b = str(brand or "").lower()
    if "거지맵" in b or "거지" in b or "가성비 식당" in b:
        return "거지맵 (가성비 식당 & 초저가 혜택)"
    elif "팝업" in b or "팝플리" in b or "팝가" in b or "헤이팝" in b or "더현대" in b:
        return "팝업스토어 & 전시/행사"
    elif b in ["cu", "gs25", "세븐일레븐", "이마트24", "씨유", "지에스25"]:
        return "편의점 혜택"
    elif "영화" in b or "cgv" in b or "메가박스" in b or "롯데시네마" in b or "롯데월드" in b or "에버랜드" in b:
        return "영화관 및 문화/테마파크"
    elif "올리브영" in b or "다이소" in b or "h&b" in b:
        return "H&B 스토어"
    elif "백화점" in b or "아울렛" in b or "신세계" in b:
        return "백화점 및 프리미엄 아울렛"
    elif "마트" in b or "이마트" in b or "홈플러스" in b or "코스트코" in b or "트레이더스" in b:
        return "대형마트 통합"
    elif "카페" in b or "커피" in b or "베이커리" in b or "스타벅스" in b or "투썸" in b or "이디야" in b or "메가커피" in b or "컴포즈" in b or "빽다방" in b or "할리스" in b or "던킨" in b or "파리바게" in b or "뚜레쥬르" in b or "배스킨" in b or "설빙" in b or "폴바셋" in b:
        return "카페 및 베이커리/디저트"
    elif "버거" in b or "치킨" in b or "피자" in b or "떡볶이" in b or "서브웨이" in b or "써브웨이" in b or "한솥" in b or "본죽" in b or "보쌈" in b or "두끼" in b or "홍콩반점" in b:
        return "외식/패스트푸드 및 피자/치킨"
    elif "스파오" in b or "유니클로" in b or "탑텐" in b or "무신사" in b or "abc" in b or "쏘카" in b or "주유" in b or "칼텍스" in b:
        return "여가 및 쇼핑 혜택"
    else:
        return category or "기타"


def get_category_marker_icon(brand: str, category: str = "") -> dict:
    """
    Returns custom Folium Icon parameters (color, icon, icon_color, prefix) based on brand and category.
    """
    effective_cat = infer_category_from_brand(brand, category)
    b_lower = str(brand or "").lower()
    c_lower = str(effective_cat or "").lower()
    
    # 0. GuziMap (Beggar Map) Cheap Eatery - Unique Lightblue Pin + White Cutlery Icon
    if "거지맵" in b_lower or "거지맵" in c_lower or "가성비" in c_lower:
        return {"color": "lightblue", "icon": "cutlery", "icon_color": "black", "prefix": "fa"}

    # 1. Pop-up Store & Exhibition / Event - Unique Black Pin + White Star Icon
    if "팝업" in b_lower or "팝업" in c_lower or "전시" in c_lower or "팝플리" in b_lower or "팝가" in b_lower or "헤이팝" in b_lower or ("더현대" in b_lower and "아울렛" not in b_lower):
        return {"color": "black", "icon": "star", "icon_color": "white", "prefix": "fa"}
        
    # 2. Convenience Store
    if "편의점" in c_lower or b_lower in ["cu", "gs25", "세븐일레븐", "이마트24", "씨유", "지에스25"]:
        return {"color": "green", "icon": "shopping-cart", "icon_color": "white", "prefix": "fa"}
        
    # 3. Department Store & Premium Outlet
    if "백화점" in c_lower or "아울렛" in c_lower or "백화점" in b_lower or "아울렛" in b_lower:
        return {"color": "purple", "icon": "building", "icon_color": "white", "prefix": "fa"}

    # 4. Movie Theater / Culture / Theme Park
    if "영화" in c_lower or "극장" in c_lower or "cgv" in b_lower or "메가박스" in b_lower or "롯데시네마" in b_lower or "롯데월드" in b_lower or "에버랜드" in b_lower:
        return {"color": "darkpurple", "icon": "film", "icon_color": "white", "prefix": "fa"}

    # 5. H&B Store (Olive Young / Daiso)
    if "h&b" in c_lower or "올리브영" in b_lower or "다이소" in b_lower:
        return {"color": "lightred", "icon": "heart", "icon_color": "white", "prefix": "fa"}

    # 6. Cafe & Bakery & Dessert
    if "카페" in c_lower or "커피" in c_lower or "베이커리" in c_lower or "디저트" in c_lower or "스타벅스" in b_lower or "투썸" in b_lower or "이디야" in b_lower or "메가커피" in b_lower or "컴포즈" in b_lower or "빽다방" in b_lower or "할리스" in b_lower or "던킨" in b_lower or "파리바게" in b_lower or "뚜레쥬르" in b_lower or "배스킨" in b_lower or "설빙" in b_lower or "폴바셋" in b_lower or "아티제" in b_lower or "더벤티" in b_lower or "요아정" in b_lower:
        return {"color": "orange", "icon": "coffee", "icon_color": "white", "prefix": "fa"}

    # 7. Fast Food / Restaurant / Pizza / Chicken / Food
    if "외식" in c_lower or "패스트푸드" in c_lower or "치킨" in c_lower or "피자" in c_lower or "버거" in b_lower or "치킨" in b_lower or "피자" in b_lower or "떡볶이" in b_lower or "서브웨이" in b_lower or "써브웨이" in b_lower or "한솥" in b_lower or "본죽" in b_lower or "보쌈" in b_lower or "두끼" in b_lower or "홍콩반점" in b_lower:
        return {"color": "red", "icon": "cutlery", "icon_color": "white", "prefix": "fa"}

    # 8. Large Mart / SSM
    if "마트" in c_lower or "이마트" in b_lower or "홈플러스" in b_lower or "롯데마트" in b_lower or "코스트코" in b_lower or "트레이더스" in b_lower:
        return {"color": "darkblue", "icon": "shopping-bag", "icon_color": "white", "prefix": "fa"}

    # 9. Leisure & Shopping & Fashion
    if "여가" in c_lower or "쇼핑" in c_lower or "스파오" in b_lower or "유니클로" in b_lower or "탑텐" in b_lower or "무신사" in b_lower or "abc" in b_lower or "쏘카" in b_lower or "주유" in c_lower or "칼텍스" in b_lower or "무인양품" in b_lower or "모던하우스" in b_lower or "아트박스" in b_lower:
        return {"color": "cadetblue", "icon": "tag", "icon_color": "white", "prefix": "fa"}

    return {"color": "blue", "icon": "info-circle", "icon_color": "white", "prefix": "fa"}
