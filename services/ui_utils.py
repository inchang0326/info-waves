from services.logger_utils import setup_logger

logger = setup_logger(__name__)

def get_brand_logo(brand_name: str) -> str:
    """
    Returns the real official brand logo URL (Favicon / CDN) if available online.
    Falls back to custom vibrant SVG emblems only when official online logos are unavailable or blocked by WAF.
    """
    import urllib.parse
    if not brand_name or not isinstance(brand_name, str):
        return "https://www.google.com/s2/favicons?domain=google.com&sz=128"

    brand_clean = brand_name.strip()

    # Tier 1: High-Definition Verified Real Official Brand Logos / CDNs / Domain Favicons
    official_logos = {
        # 편의점
        "CU": "https://www.google.com/s2/favicons?domain=cu.bgfretail.com&sz=128",
        "씨유": "https://www.google.com/s2/favicons?domain=cu.bgfretail.com&sz=128",
        "GS25": "https://www.google.com/s2/favicons?domain=gs25.gsretail.com&sz=128",
        "지에스": "https://www.google.com/s2/favicons?domain=gs25.gsretail.com&sz=128",

        # 패스트푸드 & 피자 & 치킨
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
        "루리웹": "https://www.google.com/s2/favicons?domain=ruliweb.com&sz=128",
        "에펨코리아": "https://www.google.com/s2/favicons?domain=fmkorea.com&sz=128",
        # 통신사 / 금융 / 커뮤니티
        "SKT": "https://www.google.com/s2/favicons?domain=tworld.co.kr&sz=128",
        "KT": "https://www.google.com/s2/favicons?domain=kt.com&sz=128",
        "유플러스": "https://www.google.com/s2/favicons?domain=lguplus.com&sz=128",
        "토스": "https://www.google.com/s2/favicons?domain=toss.im&sz=128",
        "네이버": "https://www.google.com/s2/favicons?domain=naver.com&sz=128",
        "카카오": "https://www.google.com/s2/favicons?domain=kakaocorp.com&sz=128",
        "에펨코리아": "https://www.google.com/s2/favicons?domain=fmkorea.com&sz=128",
        "뽐뿌": "https://www.google.com/s2/favicons?domain=ppomppu.co.kr&sz=128",
        "퀘이사존": "https://www.google.com/s2/favicons?domain=quasarzone.com&sz=128",
        "어미새": "https://www.google.com/s2/favicons?domain=eomisae.co.kr&sz=128",
        "쿨엔조이": "https://www.google.com/s2/favicons?domain=coolenjoy.net&sz=128",

        # 추가 브랜드 로고
        "서브웨이": "https://www.google.com/s2/favicons?domain=subway.co.kr&sz=128",
        "써브웨이": "https://www.google.com/s2/favicons?domain=subway.co.kr&sz=128",
        "노브랜드": "https://www.google.com/s2/favicons?domain=nobrandburger.com&sz=128",
        "프랭크버거": "https://www.google.com/s2/favicons?domain=frankburger.co.kr&sz=128",
        "60계치킨": "https://www.google.com/s2/favicons?domain=60chicken.co.kr&sz=128",
        "노랑통닭": "https://www.google.com/s2/favicons?domain=norangtongdak.co.kr&sz=128",
        "피자알볼로": "https://www.google.com/s2/favicons?domain=pizzaalvolo.co.kr&sz=128",
        "7번가피자": "https://www.google.com/s2/favicons?domain=7thpizza.com&sz=128",
        "엽기떡볶이": "https://www.google.com/s2/favicons?domain=yupdduk.com&sz=128",
        "한솥": "https://www.google.com/s2/favicons?domain=hsd.co.kr&sz=128",
        "두끼": "https://www.google.com/s2/favicons?domain=dookki.co.kr&sz=128",
        "역전할머니맥주": "https://www.google.com/s2/favicons?domain=yukhalman.co.kr&sz=128",
        "본죽": "https://www.google.com/s2/favicons?domain=bonif.co.kr&sz=128",
        "신전떡볶이": "https://www.google.com/s2/favicons?domain=sinjeon.co.kr&sz=128",
        "홍콩반점": "https://www.google.com/s2/favicons?domain=zzambbong.com&sz=128",
        "원할머니보쌈": "https://www.google.com/s2/favicons?domain=bossam.co.kr&sz=128",
        "더벤티": "https://www.google.com/s2/favicons?domain=theventi.co.kr&sz=128",
        "공차": "https://www.google.com/s2/favicons?domain=gong-cha.co.kr&sz=128",
        "할리스": "https://www.google.com/s2/favicons?domain=hollys.co.kr&sz=128",
        "던킨": "https://www.google.com/s2/favicons?domain=dunkindonuts.co.kr&sz=128",
        "크리스피크림": "https://www.google.com/s2/favicons?domain=lotteeatz.com&sz=128",
        "요아정": "https://www.google.com/s2/favicons?domain=yoajung.co.kr&sz=128",
        "설빙": "https://www.google.com/s2/favicons?domain=sulbing.com&sz=128",
        "폴바셋": "https://www.google.com/s2/favicons?domain=baristapaulbassett.co.kr&sz=128",
        "아티제": "https://www.google.com/s2/favicons?domain=cafeartisee.com&sz=128",
        "롯데마트": "https://www.google.com/s2/favicons?domain=lottemart.com&sz=128",
        "GS더프레시": "https://www.google.com/s2/favicons?domain=gsretail.com&sz=128",
        "이마트에브리데이": "https://www.google.com/s2/favicons?domain=emarteveryday.co.kr&sz=128",
        "무인양품": "https://www.google.com/s2/favicons?domain=muji.kr&sz=128",
        "모던하우스": "https://www.google.com/s2/favicons?domain=modernhousemall.com&sz=128",
        "아트박스": "https://www.google.com/s2/favicons?domain=poom.co.kr&sz=128",
        "스파오": "https://www.google.com/s2/favicons?domain=spao.com&sz=128",
        "ABC마트": "https://www.google.com/s2/favicons?domain=abcmart.a-rt.com&sz=128",
        "무신사": "https://www.google.com/s2/favicons?domain=musinsa.com&sz=128",
        "롯데월드": "https://www.google.com/s2/favicons?domain=lotteworld.com&sz=128",
        "에버랜드": "https://www.google.com/s2/favicons?domain=everland.com&sz=128",
        "쏘카": "https://www.google.com/s2/favicons?domain=socar.kr&sz=128",
        "GS칼텍스": "https://www.google.com/s2/favicons?domain=gscaltex.com&sz=128",

        # 팝업스토어 & 전시/행사
        "팝플리": "https://www.google.com/s2/favicons?domain=popply.co.kr&sz=128",
        "팝가": "https://www.google.com/s2/favicons?domain=popga.co.kr&sz=128",
        "더현대": "https://www.google.com/s2/favicons?domain=ehyundai.com&sz=128",
        "롯데월드몰": "https://www.google.com/s2/favicons?domain=lotteshopping.com&sz=128",
        "헤이팝": "https://www.google.com/s2/favicons?domain=heypop.kr&sz=128",
    }

    for key, logo_url in official_logos.items():
        if key in brand_clean:
            return logo_url

    # Tier 2: Fallback Vibrant Brand SVG Badges (For brands blocked by WAF or without public CDN logos)
    fallback_badges = {
        "세븐일레븐": ("7E", "#047857", "#ef4444"),
        "7-Eleven": ("7E", "#047857", "#ef4444"),
        "이마트24": ("24", "#eab308", "#0f172a"),
        "이마24": ("24", "#eab308", "#0f172a"),
        "emart24": ("24", "#eab308", "#0f172a"),
        "맘스터치": ("MT", "#d97706", "#ffffff"),
        "Momstouch": ("MT", "#d97706", "#ffffff"),
        "다이소": ("DS", "#dc2626", "#ffffff"),
        "Daiso": ("DS", "#dc2626", "#ffffff"),
        "메가박스": ("MB", "#312e81", "#ffffff"),
        "Megabox": ("MB", "#312e81", "#ffffff"),
        "엔제리너스": ("ANG", "#b45309", "#ffffff"),
    }

    for key, (text, bg_color, font_color) in fallback_badges.items():
        if key in brand_clean:
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
                f'<rect width="128" height="128" rx="28" fill="{bg_color}" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>'
                f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="{font_color}" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="800" font-size="42">{text}</text>'
                f'</svg>'
            )
            return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

    # Tier 3: Automatic English / Alphanumeric Domain Inference
    import re
    eng_match = re.search(r'[a-zA-Z0-9]{3,}', brand_clean)
    if eng_match:
        inferred_domain = f"{eng_match.group(0).lower()}.co.kr"
        return f"https://www.google.com/s2/favicons?domain={inferred_domain}&sz=128"

    # Tier 4: Dynamic Glassmorphism SVG Badge for Unlisted Brands
    display_text = brand_clean[:2] if len(brand_clean) >= 2 else brand_clean
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
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg_badge)}"

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
    fallback_url = "https://www.google.com/s2/favicons?domain=google.com&sz=128"

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
        f'onerror="this.onerror=null;this.src=\'{fallback_url}\';" '
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
        
    return f"{clean_cat} ({count}개)"


def get_category_marker_icon(brand: str, category: str = "") -> dict:
    """
    Returns custom Folium Icon parameters (color, icon, icon_color) based on brand and category.
    - 🎪 Pop-up Store & Exhibition: Pink Pin + Star Icon
    - 🏪 Convenience Store: Green Pin + Shopping-Cart Icon
    - ☕ Cafe / Bakery / Dessert: Orange Pin + Coffee Icon
    - 🍔 Fast Food / Restaurant / Pizza / Chicken: Red Pin + Cutlery Icon
    - 🛒 Mart / Department Store / Outlet: Purple Pin + Shopping-Bag Icon
    - 🎁 Leisure & Shopping: Cadetblue Pin + Tag Icon
    - 📍 Default: Blue Pin + Info-Sign Icon
    """
    b_lower = str(brand or "").lower()
    c_lower = str(category or "").lower()
    
    if "팝업" in b_lower or "팝업" in c_lower or "전시" in c_lower or "팝플리" in b_lower or "팝가" in b_lower or "헤이팝" in b_lower or "더현대" in b_lower:
        return {"color": "pink", "icon": "star", "icon_color": "white"}
    elif "편의점" in c_lower or b_lower in ["cu", "gs25", "세븐일레븐", "이마트24", "씨유"]:
        return {"color": "green", "icon": "shopping-cart", "icon_color": "white"}
    elif "카페" in c_lower or "커피" in b_lower or "디저트" in c_lower or "스타벅스" in b_lower or "투썸" in b_lower or "이디야" in b_lower or "메가" in b_lower or "컴포즈" in b_lower:
        return {"color": "orange", "icon": "coffee", "icon_color": "white"}
    elif "외식" in c_lower or "패스트푸드" in c_lower or "버거" in b_lower or "치킨" in b_lower or "피자" in b_lower or "떡볶이" in b_lower or "썹프라이즈" in b_lower:
        return {"color": "red", "icon": "cutlery", "icon_color": "white"}
    elif "마트" in c_lower or "백화점" in c_lower or "아울렛" in c_lower or "이마트" in b_lower or "홈플러스" in b_lower or "롯데마트" in b_lower or "코스트코" in b_lower:
        return {"color": "purple", "icon": "shopping-bag", "icon_color": "white"}
    elif "여가" in c_lower or "쇼핑" in c_lower or "올리브영" in b_lower or "다이소" in b_lower or "스파오" in b_lower or "abc" in b_lower:
        return {"color": "cadetblue", "icon": "tag", "icon_color": "white"}
    else:
        return {"color": "blue", "icon": "info-sign", "icon_color": "white"}
