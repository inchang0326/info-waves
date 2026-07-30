import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict
from playwright.sync_api import sync_playwright
from services.logger_utils import setup_logger

logger = setup_logger(__name__)

class AbstractScraper:
    def __init__(self, name: str):
        self.name = name

    def scrape(self) -> List[Dict[str, str]]:
        raise NotImplementedError

class GuziMapScraper(AbstractScraper):
    def __init__(self):
        super().__init__("거지맵 (저예산 식당 & 초저가 혜택)")

    def scrape(self) -> List[Dict[str, str]]:
        url = "https://lzeazgyvjzireemncjep.supabase.co/rest/v1/restaurants_public?select=*"
        supabase_key = os.getenv("GUZIMAP_API_KEY") or os.getenv("SUPABASE_KEY") or "sb_publishable_b7EOyF1IuulD2ZU-VYqtCA_2L3X6PSV"
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "User-Agent": "Mozilla/5.0"
        }
        results = []
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                for r in data:
                    name = r.get("name")
                    if not name: continue
                    menu = r.get("latest_menu_name") or "가성비 식단"
                    price = r.get("latest_price_krw")
                    price_str = f" ({price:,}원)" if price else ""
                    addr = r.get("address", "")
                    link = "https://xn--v69ak0xskm.com"
                    title = f"거지맵 가성비 식당: {menu}{price_str} | {addr}"
                    
                    results.append({
                        "target": f"거지맵 - {name}",
                        "title": title,
                        "details": link,
                        "category": "거지맵 (가성비 식당 & 초저가 혜택)",
                        "lat": float(r.get("lat")) if r.get("lat") else None,
                        "lon": float(r.get("lng")) if r.get("lng") else None,
                        "address": addr,
                        "brand": name
                    })
        except Exception as e:
            logger.exception(f"GuziMap scraping failed: {e}")
        return results

class NaverPlaceDirectScraper(AbstractScraper):
    def __init__(self, query: str, category: str):
        super().__init__(f"네이버 플레이스 직접 크롤링: {query}")
        self.query = query
        self.category = category

    def scrape(self) -> List[Dict[str, str]]:
        results = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
                    search_url = f"https://m.map.naver.com/search2/search.naver?query={self.query}"
                    page.goto(search_url, wait_until="domcontentloaded", timeout=10000)
                    
                    soup = BeautifulSoup(page.content(), 'html.parser')
                    items = soup.select('.item_tit')
                    for item in items[:3]:
                        text = item.text.strip()
                        if text:
                            results.append({
                                "target": "네이버 플레이스",
                                "title": text,
                                "details": search_url,
                                "category": self.category
                            })
                finally:
                    browser.close()
        except Exception as e:
            logger.exception(f"Naver Place scraping failed: {e}")
        return results

class RuliwebHotDealScraper(AbstractScraper):
    def __init__(self):
        super().__init__("루리웹 핫딜 게시판")

    def scrape(self) -> List[Dict[str, str]]:
        url = "https://bbs.ruliweb.com/market/board/1020"
        headers = {"User-Agent": "Mozilla/5.0"}
        results = []
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            titles = soup.select("a.deco")
            for t in titles[:3]:
                text = t.text.strip()
                if text:
                    link = t.get('href', url)
                    results.append({
                        "target": "루리웹",
                        "title": text,
                        "details": link,
                        "category": "핫딜 커뮤니티"
                    })
        except Exception as e:
            logger.exception(f"Ruliweb scraping failed: {e}")
        return results

class DynamicTopBrandsScraper(AbstractScraper):
    def __init__(self):
        super().__init__("동적 메이저 브랜드 스크래퍼 (Playwright)")

    def scrape(self) -> List[Dict[str, str]]:
        results = []
        
        # 1. 스타벅스 동적 파싱
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(user_agent="Mozilla/5.0")
                    page.goto("https://www.starbucks.co.kr/whats_new/campaign_list.do", wait_until="domcontentloaded", timeout=10000)
                    page.wait_for_selector('.campaign_list dl dt a', timeout=5000)
                    
                    items = page.evaluate(r"""
                    () => {
                        let arr = [];
                        document.querySelectorAll('.campaign_list dl dt a').forEach(a => {
                            let img = a.querySelector('img');
                            let title = img ? img.getAttribute('alt') : a.innerText;
                            let onclick = a.getAttribute('onclick');
                            let seq = onclick ? onclick.match(/goView\('(\d+)'\)/) : null;
                            let href = seq ? "https://www.starbucks.co.kr/whats_new/campaign_view.do?pro_seq=" + seq[1] : a.href;
                            if(title) arr.push({title: title.trim(), href: href});
                        });
                        return arr;
                    }
                    """)
                    for i in items[:3]:
                        results.append({"target": "스타벅스", "title": i['title'], "details": i['href'], "category": "카페 및 베이커리/디저트"})
                finally:
                    browser.close()
        except Exception as e:
            logger.exception(f"Starbucks dynamic scraping failed: {e}")

        # 2. 맥도날드 동적 파싱
        try:
            res = requests.get('https://www.mcdonalds.co.kr/kor/promotion/list.do', headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.select('.promotList ul li a')
            for a in links[:3]:
                img = a.find('img')
                title = img.get('alt', '').strip() if img else a.text.strip()
                href = a.get('href')
                if href and href.startswith('javascript:'):
                    seq = href.split("'")[1] if "'" in href else ""
                    href = f"https://www.mcdonalds.co.kr/kor/promotion/detail.do?promtNo={seq}"
                elif href and href.startswith('/'):
                    href = "https://www.mcdonalds.co.kr" + href
                results.append({"target": "맥도날드", "title": title, "details": href, "category": "외식/패스트푸드 및 피자/치킨"})
        except Exception as e:
            logger.exception(f"McDonalds dynamic scraping failed: {e}")
            
        return results

import concurrent.futures

class FallbackUrlManager:
    """
    Verifies link health for scraped event URLs and manages fallback to brand main landing page URLs.
    If an event page returns HTTP 404, 500, timeout, or does not exist,
    automatically falls back to the brand's main landing page URL.
    """
    @staticmethod
    def resolve_valid_event_url(event_url: str, fallback_url: str) -> str:
        """
        Validates event_url via fast HTTP HEAD/GET request.
        If event_url is empty, invalid, or returns 404/500/timeout,
        gracefully returns fallback_url.
        """
        if not event_url or not isinstance(event_url, str) or not (event_url.startswith("http://") or event_url.startswith("https://")):
            return fallback_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Fast HEAD check (timeout=2s)
        try:
            resp = requests.head(event_url, headers=headers, timeout=2, allow_redirects=True)
            if resp.status_code < 400:
                return event_url
        except Exception:
            pass

        # Streamed GET check (timeout=2s)
        try:
            resp = requests.get(event_url, headers=headers, timeout=2, stream=True)
            if resp.status_code < 400:
                return event_url
        except Exception:
            pass

        # Fallback to main brand page URL
        return fallback_url


import re
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def _brand_matches_title(brand: str, title: str) -> bool:
    if not brand or not title:
        return False
    title_lower = title.lower()
    brand_lower = brand.lower()

    if brand_lower in title_lower:
        return True

    clean_brand = re.sub(r'\(.*?\)', '', brand).strip()
    if clean_brand and clean_brand.lower() in title_lower:
        return True

    paren_matches = re.findall(r'\((.*?)\)', brand)
    for p in paren_matches:
        p_clean = p.strip()
        if p_clean and len(p_clean) >= 2 and p_clean.lower() in title_lower:
            return True

    descriptors = ["팝업스토어", "프리미엄아울렛", "백화점", "아울렛", "달달혜택", "유플투쁠", "T데이", "팝업", "혜택", "스토어"]
    core_brand = clean_brand
    for desc in descriptors:
        core_brand = core_brand.replace(desc, "").strip()

    if core_brand and len(core_brand) >= 2 and core_brand.lower() in title_lower:
        return True

    return False

class HybridOfficialScraper(AbstractScraper):
    def __init__(self):
        super().__init__("하이브리드 스크래퍼 (동적 실시간 핫트렌드)")
        # 대상 브랜드와 기본 메인페이지 정의 (하드코딩된 이벤트/링크 추가)
        self.brands = [
            # 편의점
            {"target": "CU", "main_url": "https://cu.bgfretail.com", "event_url": "https://cu.bgfretail.com/event/plus.do", "category": "편의점 혜택"},
            {"target": "GS25", "main_url": "https://gs25.gsretail.com", "event_url": "http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/current-events", "category": "편의점 혜택"},
            {"target": "세븐일레븐", "main_url": "https://www.7-eleven.co.kr", "event_url": "https://www.7-eleven.co.kr/event/eventList.asp", "category": "편의점 혜택"},
            {"target": "이마트24", "main_url": "https://emart24.co.kr", "event_url": "https://emart24.co.kr/event", "category": "편의점 혜택"},
            
            # 패스트푸드
            {"target": "버거킹", "main_url": "https://www.burgerking.co.kr", "event_url": "https://www.burgerking.co.kr/#/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "롯데리아", "main_url": "https://www.lotteeatz.com", "event_url": "https://www.lotteeatz.com/event/main", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "맘스터치", "main_url": "https://momstouch.co.kr", "event_url": "https://momstouch.co.kr/m/brand/event.php", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "KFC", "main_url": "https://www.kfckorea.com", "event_url": "https://www.kfckorea.com/promotion/eventList", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "맥도날드", "main_url": "https://www.mcdonalds.co.kr", "event_url": "https://www.mcdonalds.co.kr/kor/promotion/list.do", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "파파이스", "main_url": "https://www.popeyes.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            
            # 피자
            {"target": "도미노피자", "main_url": "https://web.dominos.co.kr", "event_url": "https://web.dominos.co.kr/event/list?gubun=E0200", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "파파존스", "main_url": "https://pji.co.kr", "event_url": "https://pji.co.kr/event/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "피자헛", "main_url": "https://www.pizzahut.co.kr", "event_url": "https://www.pizzahut.co.kr/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노모어피자", "main_url": "https://nomorepizza.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},

            # 치킨
            {"target": "교촌치킨", "main_url": "https://www.kyochon.com", "event_url": "https://www.kyochon.com/events/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "BBQ", "main_url": "https://bbq.co.kr", "event_url": "https://bbq.co.kr/events", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "BHC", "main_url": "https://www.bhc.co.kr", "event_url": "https://www.bhc.co.kr/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "푸라닭", "main_url": "https://www.puradakchicken.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "가마치통닭", "main_url": "https://www.gamachi.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "자담치킨", "main_url": "https://ejadam.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "굽네치킨", "main_url": "https://www.goobne.co.kr", "event_url": "https://www.goobne.co.kr/event/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "천년닭강정", "main_url": "https://1000dak.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            
            # 베이커리 / 디저트
            {"target": "파리바게뜨", "main_url": "https://www.paris.co.kr", "event_url": "https://www.paris.co.kr/promotion/", "category": "카페 및 베이커리/디저트"},
            {"target": "뚜레쥬르", "main_url": "https://www.tlj.co.kr", "event_url": "https://www.tlj.co.kr/community/event/list.asp", "category": "카페 및 베이커리/디저트"},
            {"target": "파리크라상", "main_url": "https://www.pariscroissant.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "배스킨라빈스", "main_url": "https://www.baskinrobbins.co.kr", "event_url": "https://www.baskinrobbins.co.kr/event/list.php", "category": "카페 및 베이커리/디저트"},

            # 카페 프랜차이즈
            {"target": "스타벅스", "main_url": "https://www.starbucks.co.kr", "event_url": "https://www.starbucks.co.kr/whats_new/campaign_list.do", "category": "카페 및 베이커리/디저트"},
            {"target": "메가커피", "main_url": "https://mega-mgccoffee.com", "event_url": "https://mega-mgccoffee.com/bbs/board.php?bo_table=event", "category": "카페 및 베이커리/디저트"},
            {"target": "컴포즈커피", "main_url": "https://composecoffee.com", "event_url": "https://composecoffee.com/event", "category": "카페 및 베이커리/디저트"},
            {"target": "빽다방", "main_url": "https://paikdabang.com", "event_url": "https://paikdabang.com/news/?page_type=event", "category": "카페 및 베이커리/디저트"},
            {"target": "이디야커피", "main_url": "https://www.ediya.com", "event_url": "https://www.ediya.com/contents/event.html", "category": "카페 및 베이커리/디저트"},
            {"target": "우지커피", "main_url": "https://oozycoffee.com", "category": "카페 및 베이커리/디저트"},
            {"target": "엔제리너스", "main_url": "https://www.lotteeatz.com", "event_url": "https://www.lotteeatz.com/event/main", "category": "카페 및 베이커리/디저트"},
            {"target": "매머드커피", "main_url": "https://www.mmthcoffee.com", "event_url": "https://www.mmthcoffee.com/sub/news/event.html", "category": "카페 및 베이커리/디저트"},
            {"target": "투썸플레이스", "main_url": "https://www.twosome.co.kr", "event_url": "https://www.twosome.co.kr/event/list.do", "category": "카페 및 베이커리/디저트"},
            
            # H&B 스토어
            {"target": "올리브영", "main_url": "https://www.oliveyoung.co.kr", "event_url": "https://www.oliveyoung.co.kr/store/main/getEventList.do", "category": "H&B 스토어"},
            {"target": "다이소", "main_url": "https://www.daisomall.co.kr", "event_url": "https://www.daisomall.co.kr/ds/evt/dsevt/getEventMain.do", "category": "H&B 스토어"},
            
            # 대형마트 / 아울렛 / 백화점 팝업
            {"target": "이마트", "main_url": "https://emart.ssg.com", "event_url": "https://store.emart.com/news/event.do", "category": "대형마트 통합"},
            {"target": "홈플러스", "main_url": "https://front.homeplus.co.kr", "event_url": "https://front.homeplus.co.kr/event", "category": "대형마트 통합"},
            {"target": "이마트 트레이더스", "main_url": "https://emart.ssg.com", "category": "대형마트 통합"},
            {"target": "코스트코", "main_url": "https://www.costco.co.kr", "category": "대형마트 통합"},
            {"target": "스타필드", "main_url": "https://www.starfield.co.kr", "event_url": "https://www.starfield.co.kr/coexmall/tenant/event.do", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "현대백화점", "main_url": "https://www.ehyundai.com", "event_url": "https://www.ehyundai.com/newPortal/ev/main.do", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "롯데백화점", "main_url": "https://www.lotteshopping.com", "event_url": "https://www.lotteshopping.com/branchShopGuide/shoppingNews", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "신세계백화점", "main_url": "https://www.shinsegae.com", "event_url": "https://www.shinsegae.com/shopping/event.do", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "롯데프리미엄아울렛", "main_url": "https://www.lotteshopping.com", "event_url": "https://www.lotteshopping.com/branchShopGuide/shoppingNews", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "신세계사이먼프리미엄아울렛", "main_url": "https://www.premiumoutlets.co.kr", "event_url": "https://www.premiumoutlets.co.kr/main/ko/event", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "현대프리미엄아울렛", "main_url": "https://www.ehyundai.com", "event_url": "https://www.ehyundai.com/newPortal/ev/main.do", "category": "백화점 및 프리미엄 아울렛"},
            
            # 의류 / 영화관 / 테마파크
            {"target": "유니클로", "main_url": "https://www.uniqlo.com/kr/ko/", "category": "여가 및 쇼핑 혜택"},
            {"target": "탑텐", "main_url": "https://topten10mall.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "메가박스", "main_url": "https://www.megabox.co.kr", "event_url": "https://www.megabox.co.kr/event", "category": "영화관 및 문화/테마파크"},
            {"target": "CGV", "main_url": "https://www.cgv.co.kr", "event_url": "http://cgv.co.kr/culture-event/event/", "category": "영화관 및 문화/테마파크"},
            {"target": "롯데시네마", "main_url": "https://www.lottecinema.co.kr", "event_url": "https://www.lottecinema.co.kr/NLCHS/Event", "category": "영화관 및 문화/테마파크"},
            {"target": "롯데월드", "main_url": "https://adventure.lotteworld.com", "event_url": "https://adventure.lotteworld.com/kor/price/benefit/information/list.do", "category": "영화관 및 문화/테마파크"},
            {"target": "에버랜드", "main_url": "https://www.everland.com", "event_url": "https://www.everland.com/everland/promotion", "category": "영화관 및 문화/테마파크"},
            
            # 통신사 / 금융
            {"target": "SKT T데이", "main_url": "https://sktmembership.tworld.co.kr", "category": "통신사 멤버십 혜택"},
            {"target": "KT 달달혜택", "main_url": "https://membership.kt.com", "category": "통신사 멤버십 혜택"},
            {"target": "유플투쁠", "main_url": "https://www.lguplus.com", "category": "통신사 멤버십 혜택"},
            {"target": "토스", "main_url": "https://toss.im", "category": "금융 및 앱테크"},
            {"target": "네이버페이", "main_url": "https://pay.naver.com", "event_url": "https://pay.naver.com/about/events", "category": "금융 및 앱테크"},
            {"target": "카카오페이", "main_url": "https://pay.kakao.com", "category": "금융 및 앱테크"},
            
            # 신규 검증 브랜드
            {"target": "서브웨이", "main_url": "https://www.subway.co.kr", "event_url": "https://www.subway.co.kr/eventList", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노브랜드버거", "main_url": "https://www.shinsegaefood.com/nobrandburger/", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "프랭크버거", "main_url": "https://www.frankburger.co.kr", "event_url": "https://www.frankburger.co.kr/board/bbs/board.php?bo_table=event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "60계치킨", "main_url": "https://www.60chicken.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노랑통닭", "main_url": "https://www.norangtongdak.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "피자알볼로", "main_url": "https://www.pizzaalvolo.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "7번가피자", "main_url": "https://www.7thpizza.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "동대문엽기떡볶이", "main_url": "https://www.yupdduk.com", "event_url": "https://www.yupdduk.com/event/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "한솥도시락", "main_url": "https://www.hsd.co.kr", "event_url": "https://www.hsd.co.kr/event/event_list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "역전할머니맥주", "main_url": "https://www.yeokjeonhalmae.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "본죽", "main_url": "https://www.bonif.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "신전떡볶이", "main_url": "http://www.sinjeon.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "홍콩반점0410", "main_url": "https://www.theborn.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "원할머니보쌈", "main_url": "https://bossam.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},

            {"target": "더벤티", "main_url": "https://www.theventi.co.kr", "event_url": "https://www.theventi.co.kr/new2022/news/event.html", "category": "카페 및 베이커리/디저트"},
            {"target": "공차", "main_url": "https://www.gong-cha.co.kr", "event_url": "https://www.gong-cha.co.kr/brand/board/event.php", "category": "카페 및 베이커리/디저트"},
            {"target": "할리스", "main_url": "https://www.hollys.co.kr", "event_url": "https://www.hollys.co.kr/news/event/list.do", "category": "카페 및 베이커리/디저트"},
            {"target": "던킨", "main_url": "https://www.dunkindonuts.co.kr", "event_url": "https://www.dunkindonuts.co.kr/event/list.php", "category": "카페 및 베이커리/디저트"},
            {"target": "크리스피크림도넛", "main_url": "https://www.lotteeatz.com", "event_url": "https://www.lotteeatz.com/event/main", "category": "카페 및 베이커리/디저트"},
            {"target": "요아정", "main_url": "https://www.yoajung.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "설빙", "main_url": "https://sulbing.com", "event_url": "https://sulbing.com/bbs/board.php?bo_table=event", "category": "카페 및 베이커리/디저트"},
            {"target": "폴바셋", "main_url": "https://www.baristapaulbassett.co.kr", "event_url": "https://www.baristapaulbassett.co.kr/whatsNews/event/List.pb", "category": "카페 및 베이커리/디저트"},
            {"target": "아티제", "main_url": "https://www.cafeartisee.com", "category": "카페 및 베이커리/디저트"},

            {"target": "롯데마트", "main_url": "https://www.lottemart.com", "category": "대형마트 통합"},
            {"target": "GS더프레시", "main_url": "https://www.gsretail.com", "category": "대형마트 통합"},
            {"target": "이마트에브리데이", "main_url": "https://www.emarteveryday.co.kr", "category": "대형마트 통합"},
            {"target": "무인양품", "main_url": "https://www.muji.kr", "category": "여가 및 쇼핑 혜택"},
            {"target": "모던하우스", "main_url": "https://www.modernhousemall.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "아트박스", "main_url": "https://www.poom.co.kr", "event_url": "https://www.poom.co.kr/front/event/eventList", "category": "여가 및 쇼핑 혜택"},
            {"target": "스파오", "main_url": "https://spao.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "ABC마트", "main_url": "https://abcmart.a-rt.com", "event_url": "https://abcmart.a-rt.com/promotion/event", "category": "여가 및 쇼핑 혜택"},
            {"target": "무신사스탠다드", "main_url": "https://www.musinsa.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "쏘카", "main_url": "https://www.socar.kr", "category": "여가 및 쇼핑 혜택"},
            {"target": "GS칼텍스", "main_url": "https://www.gscaltex.com", "category": "여가 및 쇼핑 혜택"},

            {"target": "뽐뿌", "main_url": "https://www.ppomppu.co.kr", "category": "핫딜 커뮤니티"},
            {"target": "퀘이사존", "main_url": "https://quasarzone.com", "category": "핫딜 커뮤니티"},
            {"target": "어미새", "main_url": "https://eomisae.co.kr", "category": "핫딜 커뮤니티"},
            {"target": "쿨엔조이", "main_url": "https://coolenjoy.net", "category": "핫딜 커뮤니티"},

            {"target": "팝플리 (POPPLY)", "main_url": "https://popply.co.kr", "category": "팝업스토어 & 전시/행사"},
            {"target": "팝가 (POPGA)", "main_url": "https://popga.co.kr", "category": "팝업스토어 & 전시/행사"},
            {"target": "헤이팝 (heyPOP)", "main_url": "https://heypop.kr", "category": "팝업스토어 & 전시/행사"}
        ]

    def _fetch_dynamic_event_info(self, brand_info: Dict[str, str]) -> Dict[str, str]:
        brand = brand_info["target"]
        main_url = brand_info["main_url"]
        category = brand_info["category"]
        event_url = brand_info.get("event_url")
        
        event_title = None
        event_desc = None
        
        try:
            encoded_brand = urllib.parse.quote(brand)
            url = f"https://news.google.com/rss/search?q={encoded_brand}+이벤트+OR+할인+OR+세일+OR+프로모션+when:30d&hl=ko&gl=KR&ceid=KR:ko"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'xml')
                items = soup.find_all('item')
                for item in items:
                    title_elem = item.find('title')
                    if title_elem:
                        title = title_elem.text.split(" - ")[0].strip()
                        if _brand_matches_title(brand, title):
                            event_title = f"✨ [실시간 혜택] {title}"
                            desc_elem = item.find('description')
                            if desc_elem:
                                desc_soup = BeautifulSoup(desc_elem.text, 'html.parser')
                                event_desc = desc_soup.get_text(strip=True)[:150]
                            break
        except Exception as e:
            logger.debug(f"RSS fetch failed for {brand}: {e}")

        # R1: 브랜드 공식 이벤트 페이지 직접 연결 (하드코딩된 event_url 우선)
        final_title = event_title if event_title else f"{brand} 상시 혜택 및 이벤트 (공식 홈페이지 참조)"
        
        # 유효성 검사 (FallbackUrlManager) - 메인 홈페이지 유효성 체크
        validated_url = FallbackUrlManager.resolve_valid_event_url(main_url, main_url)
        
        res = {
            "target": brand,
            "title": final_title,
            "details": validated_url,
            "category": category,
            "fallback_used": "true"
        }
        
        if event_url:
            # 뉴스 기사 URL 대신 공식 이벤트 페이지 URL을 source_url로 할당
            res["source_url"] = event_url
            
        if event_desc:
            res["description"] = event_desc
            
        return res

    def scrape(self) -> List[Dict[str, str]]:
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            fetched_items = list(executor.map(self._fetch_dynamic_event_info, self.brands))
            for item in fetched_items:
                if item:
                    results.append(item)
                    
        # 거지맵 병합
        try:
            guzi_items = GuziMapScraper().scrape()
            if guzi_items:
                results.extend(guzi_items)
        except Exception as e:
            logger.exception(f"GuziMap fetch error: {e}")

        return results

