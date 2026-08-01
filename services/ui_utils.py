from services.logger_utils import setup_logger

logger = setup_logger(__name__)

def get_brand_logo(brand_name: str) -> str:
    """
    Returns the real official brand logo URL (Favicon / CDN) if available online as primary default.
    """
    if not brand_name or not isinstance(brand_name, str):
        return "https://www.google.com/s2/favicons?domain=google.com&sz=128"

    brand_clean = brand_name.strip()

    official_logos = {
        # 편의점
        "CU": "https://www.google.com/s2/favicons?domain=cu.bgfretail.com&sz=128",
        "씨유": "https://www.google.com/s2/favicons?domain=cu.bgfretail.com&sz=128",
        "GS25": "https://www.google.com/s2/favicons?domain=gs25.gsretail.com&sz=128",
        "지에스": "https://www.google.com/s2/favicons?domain=gs25.gsretail.com&sz=128",

        # 패스트푸드 & 버거 & 피자 & 치킨
        "맥도날드": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/mcdonalds.svg",
        "McDonald": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/mcdonalds.svg",
        "버거킹": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/burgerking.svg",
        "Burger King": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/burgerking.svg",
        "KFC": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kfc.svg",
        "케이에프씨": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kfc.svg",
        "롯데리아": "https://www.google.com/s2/favicons?domain=lotteeatz.com&sz=128",
        "Lotteria": "https://www.google.com/s2/favicons?domain=lotteeatz.com&sz=128",
        "도미노피자": "https://www.google.com/s2/favicons?domain=dominos.co.kr&sz=128",
        "도미노": "https://www.google.com/s2/favicons?domain=dominos.co.kr&sz=128",
        "피자헛": "https://www.google.com/s2/favicons?domain=pizzahut.co.kr&sz=128",
        "교촌치킨": "https://www.google.com/s2/favicons?domain=kyochon.com&sz=128",
        "교촌": "https://www.google.com/s2/favicons?domain=kyochon.com&sz=128",
        "BBQ": "https://www.google.com/s2/favicons?domain=bbq.co.kr&sz=128",
        "BHC": "https://www.google.com/s2/favicons?domain=bhc.co.kr&sz=128",
        "굽네치킨": "https://www.google.com/s2/favicons?domain=goobne.co.kr&sz=128",
        "파파존스": "https://www.google.com/s2/favicons?domain=papajohns.com&sz=128",

        # 카페 / 베이커리 / 디저트
        "스타벅스": "https://www.google.com/s2/favicons?domain=starbucks.co.kr&sz=128",
        "Starbucks": "https://www.google.com/s2/favicons?domain=starbucks.co.kr&sz=128",
        "투썸플레이스": "https://www.google.com/s2/favicons?domain=twosome.co.kr&sz=128",
        "투썸": "https://www.google.com/s2/favicons?domain=twosome.co.kr&sz=128",
        "이디야커피": "https://www.google.com/s2/favicons?domain=ediya.com&sz=128",
        "이디야": "https://www.google.com/s2/favicons?domain=ediya.com&sz=128",
        "메가커피": "https://www.google.com/s2/favicons?domain=mega-mgccoffee.com&sz=128",
        "메가MGC": "https://www.google.com/s2/favicons?domain=mega-mgccoffee.com&sz=128",
        "컴포즈커피": "https://www.google.com/s2/favicons?domain=composecoffee.com&sz=128",
        "컴포즈": "https://www.google.com/s2/favicons?domain=composecoffee.com&sz=128",
        "빽다방": "https://www.google.com/s2/favicons?domain=paikdabang.com&sz=128",
        "파리바게뜨": "https://www.google.com/s2/favicons?domain=paris.co.kr&sz=128",
        "파리바게트": "https://www.google.com/s2/favicons?domain=paris.co.kr&sz=128",
        "파리크라상": "https://www.google.com/s2/favicons?domain=paris.co.kr&sz=128",
        "뚜레쥬르": "https://www.google.com/s2/favicons?domain=tlj.co.kr&sz=128",
        "배스킨라빈스": "https://www.google.com/s2/favicons?domain=baskinrobbins.co.kr&sz=128",

        # H&B / 유통 / 의류 / 영화관 / IT
        "올리브영": "https://www.google.com/s2/favicons?domain=oliveyoung.co.kr&sz=128",
        "Olive Young": "https://www.google.com/s2/favicons?domain=oliveyoung.co.kr&sz=128",
        "홈플러스": "https://www.google.com/s2/favicons?domain=homeplus.co.kr&sz=128",
        "Homeplus": "https://www.google.com/s2/favicons?domain=homeplus.co.kr&sz=128",
        "이마트": "https://www.google.com/s2/favicons?domain=emart.ssg.com&sz=128",
        "코스트코": "https://www.google.com/s2/favicons?domain=costco.co.kr&sz=128",
        "신세계": "https://www.google.com/s2/favicons?domain=shinsegae.com&sz=128",
        "현대백화점": "https://www.google.com/s2/favicons?domain=ehyundai.com&sz=128",
        "롯데백화점": "https://www.google.com/s2/favicons?domain=lotteshopping.com&sz=128",
        "스타필드": "https://www.google.com/s2/favicons?domain=starfield.co.kr&sz=128",
        "유니클로": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/uniqlo.svg",
        "Uniqlo": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/uniqlo.svg",
        "탑텐": "https://www.google.com/s2/favicons?domain=topten10mall.com&sz=128",
        "CGV": "https://www.google.com/s2/favicons?domain=cgv.co.kr&sz=128",
        "롯데시네마": "https://www.google.com/s2/favicons?domain=lottecinema.co.kr&sz=128",

        # 통신사 / 금융 / 커뮤니티
        "SKT": "https://www.google.com/s2/favicons?domain=tworld.co.kr&sz=128",
        "KT": "https://www.google.com/s2/favicons?domain=kt.com&sz=128",
        "유플러스": "https://www.google.com/s2/favicons?domain=lguplus.com&sz=128",
        "유플투쁠": "https://www.google.com/s2/favicons?domain=lguplus.com&sz=128",
        "토스": "https://www.google.com/s2/favicons?domain=toss.im&sz=128",
        "네이버": "https://www.google.com/s2/favicons?domain=naver.com&sz=128",
        "카카오": "https://www.google.com/s2/favicons?domain=kakaocorp.com&sz=128",

        # 추가 브랜드
        "서브웨이": "https://www.google.com/s2/favicons?domain=subway.co.kr&sz=128",
        "써브웨이": "https://www.google.com/s2/favicons?domain=subway.co.kr&sz=128",
        "노브랜드버거": "https://www.google.com/s2/favicons?domain=shinsegaefood.com&sz=128",
        "프랭크버거": "https://www.google.com/s2/favicons?domain=frankburger.co.kr&sz=128",
        "60계치킨": get_brand_fallback_badge("60계치킨"),
        "천년닭강정": get_brand_fallback_badge("천년닭강정"),
        "동대문엽기떡볶이": get_brand_fallback_badge("동대문엽기떡볶이"),
        "엽기떡볶이": get_brand_fallback_badge("동대문엽기떡볶이"),
        "한솥도시락": get_brand_fallback_badge("한솥도시락"),
        "한솥": get_brand_fallback_badge("한솥도시락"),
        "역전할머니맥주": get_brand_fallback_badge("역전할머니맥주"),
        "신전떡볶이": get_brand_fallback_badge("신전떡볶이"),
        "할리스": get_brand_fallback_badge("할리스"),
        "GS더프레시": get_brand_fallback_badge("GS더프레시"),
        "무인양품": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/muji.svg",
        "롯데월드": get_brand_fallback_badge("롯데월드"),
    }

    for key, logo_url in official_logos.items():
        if key in brand_clean:
            return logo_url

    # Fallback to automatic domain inference
    import re
    eng_match = re.search(r'[a-zA-Z0-9]{3,}', brand_clean)
    if eng_match:
        inferred_domain = f"{eng_match.group(0).lower()}.co.kr"
        return f"https://www.google.com/s2/favicons?domain={inferred_domain}&sz=128"

    return get_brand_fallback_badge(brand_name)


def get_brand_fallback_badge(brand_name: str) -> str:
    """
    Returns custom vibrant SVG Base64 badge as a 100% reliable fallback target for onerror events.
    """
    import base64

    if not brand_name or not isinstance(brand_name, str):
        display_text = "?"
    else:
        brand_clean = brand_name.strip()
        display_text = brand_clean[:2] if len(brand_clean) >= 2 else brand_clean

    fallback_badges = {
        "CU": ("CU", "#652d90", "#00a88f"),
        "GS25": ("GS25", "#007bc4", "#ffffff"),
        "세븐일레븐": ("7E", "#047857", "#ef4444"),
        "이마트24": ("24", "#eab308", "#0f172a"),
        "맥도날드": ("M", "#da291c", "#ffbc0d"),
        "버거킹": ("BK", "#d72300", "#fbe122"),
        "KFC": ("KFC", "#e4002b", "#ffffff"),
        "롯데리아": ("L", "#ed1c24", "#ffffff"),
        "맘스터치": ("MT", "#d97706", "#ffffff"),
        "서브웨이": ("SUB", "#008a38", "#ffc72c"),
        "노브랜드버거": ("NBB", "#ffb800", "#000000"),
        "도미노피자": ("DP", "#0078ac", "#e31837"),
        "피자헛": ("PH", "#ee3124", "#ffffff"),
        "교촌치킨": ("교촌", "#c69214", "#ffffff"),
        "BBQ": ("BBQ", "#d32f2f", "#ffffff"),
        "BHC": ("bhc", "#ff8c00", "#ffffff"),
        "60계치킨": ("60계", "#d97706", "#ffffff"),
        "천년닭강정": ("천년", "#ea580c", "#ffffff"),
        "동대문엽기떡볶이": ("엽떡", "#dc2626", "#fef08a"),
        "한솥도시락": ("한솥", "#f97316", "#ffffff"),
        "신전떡볶이": ("신전", "#b91c1c", "#ffffff"),
        "역전할머니맥주": ("역전", "#ca8a04", "#ffffff"),
        "스타벅스": ("스벅", "#00704a", "#ffffff"),
        "투썸플레이스": ("투썸", "#111827", "#ef4444"),
        "이디야커피": ("이디야", "#00205b", "#ffffff"),
        "메가커피": ("메가", "#fbbf24", "#1e3a8a"),
        "컴포즈커피": ("컴포즈", "#f59e0b", "#000000"),
        "빽다방": ("빽다방", "#1d4ed8", "#facc15"),
        "파리바게뜨": ("파바", "#002b49", "#ffffff"),
        "배스킨라빈스": ("BR", "#ff007f", "#0099ff"),
        "할리스": ("HL", "#ba1b22", "#ffffff"),
        "올리브영": ("올영", "#70b22d", "#ffffff"),
        "다이소": ("DS", "#dc2626", "#ffffff"),
        "이마트": ("이마트", "#ffb800", "#000000"),
        "홈플러스": ("홈플", "#e11d48", "#ffffff"),
        "GS더프레시": ("GS", "#059669", "#ffffff"),
        "무인양품": ("MUJI", "#7f1d1d", "#ffffff"),
        "CGV": ("CGV", "#ed1c24", "#ffffff"),
        "메가박스": ("MB", "#312e81", "#ffffff"),
        "롯데월드": ("LW", "#6b21a8", "#fde047"),
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
    - R2: Displays detailed popup store event description, status badge, operating hours, and links.
    """
    logo_url = get_brand_logo(brand)
    fallback_badge = get_brand_fallback_badge(brand)

    href = link if (link and link.startswith("http")) else f"https://search.naver.com/search.naver?query={html.escape(link or brand)}"
    if "xn--v69ak0xskm.com" in href:
        target_item = (branches[0] if (branches and len(branches) > 0) else None)
        if target_item and target_item.get("lat") and target_item.get("lon"):
            import urllib.parse
            href = f"https://map.kakao.com/link/map/{urllib.parse.quote(brand)},{target_item.get('lat')},{target_item.get('lon')}"
        elif target_item and target_item.get("address"):
            import urllib.parse
            search_query = f"{brand} {target_item.get('address')}".strip()
            href = f"https://map.kakao.com/link/search/{urllib.parse.quote(search_query)}"

    escaped_brand = html.escape(str(brand or ""))
    escaped_title = html.escape(str(title or ""))

    # Event details block for popup store items
    event_details_html = ""
    target_item = (branches[0] if (branches and len(branches) > 0) else None)
    if target_item and target_item.get("description"):
        desc = html.escape(str(target_item.get("description", "")))
        status = html.escape(str(target_item.get("event_status", "🔥 진행중")))
        schedule = html.escape(str(target_item.get("schedule", "")))
        content = html.escape(str(target_item.get("event_content", "")))
        src_url = target_item.get("source_url") or href

        schedule_block = f'<div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">📅 {schedule}</div>' if schedule else ''
        content_block = f'<div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">🏷️ {content}</div>' if content else ''

        event_details_html = (
            f'<div class="event-details-box" style="margin-top: 12px; padding: 12px; background: rgba(254, 243, 199, 0.15); border: 1px solid rgba(217, 119, 6, 0.3); border-radius: 12px;">'
            f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">'
            f'<span style="background: #FEF3C7; color: #D97706; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{status}</span>'
            f'<a href="{src_url}" target="_blank" rel="noopener noreferrer" style="font-size: 12px; color: #059669; font-weight: 700; text-decoration: none;">🔗 행사 소식</a>'
            f'</div>'
            f'<div style="font-size: 13px; font-weight: 600; color: var(--text-main); line-height: 1.4;">{desc}</div>'
            f'{schedule_block}'
            f'{content_block}'
            f'</div>'
        )

    # Branch section: collapsible "주변 매칭"
    branches_html = ""
    if branches:
        import urllib.parse
        branch_items = ""
        for b in branches:
            name = html.escape(str(b.get('target', '')))
            road_addr = str(b.get('road_address', '') or b.get('address', ''))
            # Escape special characters for safe JS/HTML embedding
            safe_addr = road_addr.replace('"', '&quot;').replace("'", "&#39;").replace('\n', ' ').replace('\r', '')
            
            if road_addr:
                lat = b.get("lat")
                lon = b.get("lon")
                if lat and lon:
                    kakaomap_link = f"https://map.kakao.com/link/map/{urllib.parse.quote(name)},{lat},{lon}"
                else:
                    search_query = f"{name} {road_addr}".strip()
                    kakaomap_link = f"https://map.kakao.com/link/search/{urllib.parse.quote(search_query)}"
                branch_items += (
                    f'<div class="branch-item" style="cursor:pointer;">'
                    f'<div class="branch-name" style="display:flex; justify-content:space-between; align-items:center;">'
                    f'<span>{name}</span>'
                    f'<div>'
                    f'<span class="copy-addr-btn" data-addr="{safe_addr}" style="font-size:12px; color:#3B82F6; font-weight:600; padding:2px 4px;">주소 복사</span>'
                    f'<a href="{kakaomap_link}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, \'_blank\', \'noopener,noreferrer\'); return false;" style="font-size:12px; color:#10B981; font-weight:600; padding:2px 4px; text-decoration:none; margin-left:4px;">바로 가기</a>'
                    f'</div>'
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

    safe_item = target_item or {}
    contents = (html.escape(str(safe_item.get("description", ""))) + " " + html.escape(str(safe_item.get("event_content", "")))).strip()
    contents = contents or escaped_title
    category = (branches[0].get("category", "") if branches and len(branches) > 0 else "")
    hide_logo = category in ["추천 맛집", "가볼만한 곳", "대형 이벤트", "거지맵 (가성비 식당 & 초저가 혜택)", "팝업스토어 & 전시/행사"]

    if hide_logo:
        header_content = f'<div style="font-size: 16px; font-weight: 800; color: var(--text-main); padding-bottom: 8px;">{escaped_brand or "이름 없음"}</div>'
    else:
        header_content = (
            f'<img src="{logo_url}" '
            f'onerror="this.onerror=null;this.src=\'{fallback_badge}\';" '
            f'class="info-card-logo" alt="{escaped_brand}" referrerpolicy="no-referrer" />'
        )

    card_html = (
        f'<div id="{card_id}" class="info-card">'

        # Clickable area: logo + brand + title → opens detail link in a new window
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, \'_blank\', \'noopener,noreferrer\'); return false;" class="info-card-link">'

        # Card header: logo + brand name
        f'<div class="info-card-header">'
        f'{header_content}'
        f'</div>'

        # Card body: title
        f'<div class="info-card-title">{contents}</div>'

        + f'</a>'

        # Branch section: outside the link, collapsible
        + (f'<div class="info-card-branches">{branches_html}</div>' if branches_html else '')

        + f'</div>'
    )
    return card_html


def generate_mini_popup_html(brand: str, title: str, link: str, item_dict: dict = None) -> str:
    """
    Generates a lightweight, inline-styled HTML for Folium Map Popups with R2 Popup event detail support.
    """
    import urllib.parse
    logo_url = get_brand_logo(brand)
    fallback_url = get_brand_fallback_badge(brand)
    href = link if (link and link.startswith("http")) else f"https://search.naver.com/search.naver?query={html.escape(link or brand)}"
    escaped_brand = html.escape(str(brand or ""))
    escaped_title = html.escape(str(title or ""))
    
    kakaomap_btn = ""
    show_detail_btn = True
    if item_dict:
        lat = item_dict.get("lat")
        lon = item_dict.get("lon")
        address = str(item_dict.get("road_address") or item_dict.get("address") or "")
        kakaomap_link = ""
        if lat and lon:
            kakaomap_link = f"https://map.kakao.com/link/map/{urllib.parse.quote(brand)},{lat},{lon}"
        elif address:
            search_query = f"{brand} {address}".strip()
            kakaomap_link = f"https://map.kakao.com/link/search/{urllib.parse.quote(search_query)}"
            
        if kakaomap_link:
            kakaomap_btn = f'<a href="{kakaomap_link}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, \'_blank\', \'noopener,noreferrer\'); return false;" style="font-size: 12px; color: #10B981; text-decoration: none; font-weight: 700;">바로 가기</a>'
            
        if item_dict.get("category") in ["주변 추천 맛집", "주변 가볼만한 곳"]:
            show_detail_btn = False
            
        if item_dict.get("category") and "거지맵" in item_dict.get("category", ""):
            href = kakaomap_link
            kakaomap_btn = ""

        if item_dict.get("category") and "팝업스토어" in item_dict.get("category", ""):
            if item_dict.get("source_url"):
                href = item_dict["source_url"]

    detail_btn = f'<a href="{href}" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, \'_blank\', \'noopener,noreferrer\'); return false;" style="font-size: 12px; color: #2563EB; text-decoration: none; font-weight: 700;">자세히 보기</a>' if show_detail_btn else ""
    
    if item_dict and item_dict.get("description"):
        desc = html.escape(str(item_dict.get("description", "")))
        
        category = item_dict.get("category", "")
        hide_logo = category in ["추천 맛집", "가볼만한 곳", "대형 이벤트", "거지맵 (가성비 식당 & 초저가 혜택)", "팝업스토어 & 전시/행사"]
        if hide_logo:
            logo_html = ""
        else:
            logo_html = f'<img src="{logo_url}" onerror="this.onerror=null;this.src=\'{fallback_url}\';" style="width: 24px; height: 24px; border-radius: 6px; margin-right: 8px; border: 1px solid #e5e7eb; object-fit: contain; background: white;" />'

        return f"""
        <div style="font-family: 'Pretendard', -apple-system, sans-serif; min-width: 220px; padding: 6px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                {logo_html}
                <strong style="font-size: 14px; color: #111827;">{escaped_brand}</strong>
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #1F2937; margin-bottom: 8px; line-height: 1.4; word-break: keep-all;">
                {desc}
            </div>
            <div style="display: flex; gap: 8px;">
                {detail_btn}
                {kakaomap_btn}
            </div>
        </div>
        """

    return f"""
    <div style="font-family: 'Pretendard', -apple-system, sans-serif; min-width: 200px; padding: 4px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <img src="{logo_url}" onerror="this.onerror=null;this.src='{fallback_url}';" style="width: 24px; height: 24px; border-radius: 6px; margin-right: 8px; border: 1px solid #e5e7eb; object-fit: contain; background: white;" />
            <strong style="font-size: 14px; color: #111827;">{escaped_brand}</strong>
        </div>
        <div style="font-size: 13px; color: #4B5563; margin-bottom: 12px; line-height: 1.4; word-break: keep-all;">
            {escaped_title}
        </div>
        <div style="display: flex; gap: 8px;">
            {detail_btn}
            {kakaomap_btn}
        </div>
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
    
    # 0. GuziMap (Beggar Map) Cheap Eatery - Unique Black Pin + Yellow Cutlery Icon
    if "거지맵" in b_lower or "거지맵" in c_lower or "가성비" in c_lower:
        return {"color": "black", "icon": "cutlery", "icon_color": "yellow", "prefix": "fa"}

    # 1. Pop-up Store & Exhibition / Event - Unique Black Pin + Yellow Star Icon
    if "팝업" in b_lower or "팝업" in c_lower or "전시" in c_lower or "팝플리" in b_lower or "팝가" in b_lower or "헤이팝" in b_lower or ("더현대" in b_lower and "아울렛" not in b_lower):
        return {"color": "black", "icon": "star", "icon_color": "yellow", "prefix": "fa"}
        
    # 2. Convenience Store
    if "편의점" in c_lower or b_lower in ["cu", "gs25", "세븐일레븐", "이마트24", "씨유", "지에스25"]:
        return {"color": "green", "icon": "shopping-cart", "icon_color": "white", "prefix": "fa"}
        
    # 3. Department Store & Premium Outlet
    if "백화점" in c_lower or "아울렛" in c_lower or "백화점" in b_lower or "아울렛" in b_lower:
        return {"color": "purple", "icon": "gift", "icon_color": "white", "prefix": "fa"}

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
        return {"color": "cadetblue", "icon": "shopping-bag", "icon_color": "white", "prefix": "fa"}

    return {"color": "blue", "icon": "info-circle", "icon_color": "white", "prefix": "fa"}
