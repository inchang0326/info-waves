import requests
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
                page = browser.new_page(user_agent="Mozilla/5.0")
                page.goto("https://www.starbucks.co.kr/whats_new/campaign_list.do", wait_until="domcontentloaded", timeout=10000)
                page.wait_for_selector('.campaign_list dl dt a', timeout=5000)
                
                items = page.evaluate("""
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

class HybridOfficialScraper(AbstractScraper):
    def __init__(self):
        super().__init__("하이브리드 스크래퍼 (시그니처 + 실시간 핫트렌드)")
        
    def _fetch_news_headline(self, brand: str) -> str:
        try:
            url = f"https://news.google.com/rss/search?q={brand}+이벤트+when:30d&hl=ko&gl=KR&ceid=KR:ko"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'xml')
                items = soup.find_all('item')
                for item in items:
                    title = item.title.text.split(" - ")[0].strip()
                    # 필터링: 브랜드명이 포함된 기사를 선호하고 너무 뻔한 제목 배제
                    if brand in title or "이벤트" in title or "할인" in title or "프로모션" in title or "세일" in title:
                        return f" & [신규] {title}"
        except Exception:
            pass
        return ""

    def scrape(self) -> List[Dict[str, str]]:
        base_data = [
            # 편의점
            {"target": "CU", "title": "쓔퍼세일 & 이달의 1+1/2+1 득템 혜택", "details": "https://cu.bgfretail.com/event/plus.do?category=event", "category": "편의점 혜택"},
            {"target": "GS25", "title": "갓세일 & 나만의냉장고 1+1 기획전", "details": "https://gs25.gsretail.com/gscvs/ko/products/event-goods", "category": "편의점 혜택"},
            {"target": "세븐일레븐", "title": "세븐일레븐데이 & 이달의 와인장터 혜택", "details": "https://www.7-eleven.co.kr/product/presentList.asp", "category": "편의점 혜택"},
            {"target": "이마트24", "title": "이달의 반값 할인 & 1+1 정기행사", "details": "https://emart24.co.kr/goods/event", "category": "편의점 혜택"},
            
            # 패스트푸드
            {"target": "버거킹", "title": "와퍼주니어 반값 & 올데이킹(ALL DAY KING) 혜택", "details": "https://www.burgerking.co.kr/#/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "롯데리아", "title": "리아데이(특정일) & 든든점심 할인 이벤트", "details": "https://www.lotteeatz.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "맘스터치", "title": "싸이데이 & 이달의 신메뉴 무료 세트업 프로모션", "details": "https://momstouch.co.kr/brand/notice/", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "KFC", "title": "매월 11일 치킨올데이(1+1) & 징거벨 오더 혜택", "details": "https://www.kfckorea.com/promotion", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "맥도날드", "title": "맥런치 할인 & 해피스낵 타임 혜택", "details": "https://www.mcdonalds.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "파파이스", "title": "슈퍼스타팩 할인 & 이달의 스페셜 콤보 프로모션", "details": "https://www.popeyes.co.kr/event", "category": "외식/패스트푸드 및 피자/치킨"},
            
            # 피자
            {"target": "도미노피자", "title": "화요일 방문포장 40% & 도미노스데이 할인", "details": "https://web.dominos.co.kr/event/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "파파존스", "title": "매주 금요일 파파프라이데이(1+1) & 이달의 신메뉴 할인", "details": "https://pji.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "피자헛", "title": "배달 20% 포장 30% 상시할인 & 오늘의 피자 혜택", "details": "https://www.pizzahut.co.kr/cs/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노모어피자", "title": "포장 할인 혜택 & 요일별 특가 프로모션", "details": "https://nomorepizza.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},

            # 치킨
            {"target": "교촌치킨", "title": "교촌앱 멤버십(방문포장) 혜택 & 이달의 세트 할인", "details": "https://www.kyochon.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "BBQ", "title": "BBQ앱 황금올리브 반값 & 쿠폰 프로모션", "details": "https://bbq.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "BHC", "title": "뿌링클 데이 & 자사앱 배달/포장 특별 할인", "details": "https://www.bhc.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "푸라닭", "title": "푸라닭 한정판 굿즈 이벤트 & 방문포장 할인", "details": "https://www.puradakchicken.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "가마치통닭", "title": "두 마리 포장 할인 특가 & 치맥 프로모션", "details": "https://www.gamachi.co.kr/event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "자담치킨", "title": "맵슐랭/티키타코 신메뉴 세트 할인 혜택", "details": "https://ejadam.co.kr/bbs/board.php?bo_table=event", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "굽네치킨", "title": "고추바사삭 할인 기획전 & 배달앱 제휴 프로모션", "details": "https://www.goobne.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "천년닭강정", "title": "패밀리 사이즈 포장 할인 & 배달 리뷰 이벤트", "details": "https://search.naver.com/search.naver?query=%EC%B2%A3%EB%85%84%EB%8B%AD%EA%B0%95%EC%A0%95", "category": "외식/패스트푸드 및 피자/치킨"},
            
            # 베이커리 / 디저트
            {"target": "파리바게뜨", "title": "매월 1일 파바데이 & 해피오더 픽업 할인", "details": "https://www.paris.co.kr/promotion", "category": "카페 및 베이커리/디저트"},
            {"target": "뚜레쥬르", "title": "SKT/KT 통신사 멤버십 최대 30% 할인 & 뚜데이", "details": "https://www.tlj.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "파리크라상", "title": "해피포인트 적립 이벤트 & 프리미엄 케이크 예약 혜택", "details": "https://www.pariscroissant.co.kr/", "category": "카페 및 베이커리/디저트"},
            {"target": "배스킨라빈스", "title": "매월 31일 31Day 사이즈업 & 이달의 맛 할인", "details": "https://www.baskinrobbins.co.kr/menu/list.php?top=C&sub=A", "category": "카페 및 베이커리/디저트"},

            # 카페 프랜차이즈
            {"target": "스타벅스", "title": "별다방 클래스 & e-프리퀀시 이벤트", "details": "https://www.starbucks.co.kr/whats_new/campaign_list.do", "category": "카페 및 베이커리/디저트"},
            {"target": "메가커피", "title": "메가오더 픽업 할인 & 이달의 신메뉴 타임세일", "details": "https://mega-mgccoffee.com/news/", "category": "카페 및 베이커리/디저트"},
            {"target": "컴포즈커피", "title": "컴포즈 앱 멤버십 쿠폰 & 신메뉴 할인 프로모션", "details": "https://composecoffee.com/event", "category": "카페 및 베이커리/디저트"},
            {"target": "빽다방", "title": "빽다방 앱 스탬프 적립 & 앗!메리카노 특가", "details": "https://paikdabang.com/news/", "category": "카페 및 베이커리/디저트"},
            {"target": "이디야커피", "title": "이디야 멤버스 스탬프 쿠폰 & 이달의 콜라보 혜택", "details": "https://www.ediya.com/contents/event.html", "category": "카페 및 베이커리/디저트"},
            {"target": "우지커피", "title": "앱 오더 할인 쿠폰 & 시즌 한정 음료 이벤트", "details": "https://search.naver.com/search.naver?query=%EC%9A%B0%EC%A7%80%EC%BB%A4%ED%94%B9", "category": "카페 및 베이커리/디저트"},
            {"target": "엔제리너스", "title": "롯데잇츠 앱 쿠폰 & 네고왕 반값 프로모션", "details": "https://www.lotteeatz.com", "category": "카페 및 베이커리/디저트"},
            {"target": "매머드커피", "title": "매머드오더 선결제 할인 & 대용량 사이즈업 특가", "details": "https://www.mmthcoffee.com", "category": "카페 및 베이커리/디저트"},
            {"target": "투썸플레이스", "title": "투썸하트 피스케이크 증정 & 시즌 음료 혜택", "details": "https://www.twosome.co.kr", "category": "카페 및 베이커리/디저트"},
            
            # H&B 스토어
            {"target": "올리브영", "title": "올영세일(분기별) & 올리브영 데이(매월 25~27일)", "details": "https://www.oliveyoung.co.kr/store/main/getSaleList.do", "category": "H&B 스토어"},
            {"target": "다이소", "title": "다이소 신상탐험대 & 품절대란템 기획전", "details": "https://www.daisomall.co.kr", "category": "H&B 스토어"},
            
            # 대형마트 / 아울렛 / 백화점 팝업
            {"target": "이마트", "title": "이마트 쓱세일 & 주말 반값 타임세일 전단지", "details": "https://emart.ssg.com", "category": "대형마트 통합"},
            {"target": "홈플러스", "title": "홈플런 대란 & 몰빵데이 주말 파격 세일", "details": "https://front.homeplus.co.kr/event", "category": "대형마트 통합"},
            {"target": "이마트 트레이더스", "title": "트레이더스 클럽 멤버십 특가 & 대용량 할인 기획전", "details": "https://emart.ssg.com", "category": "대형마트 통합"},
            {"target": "코스트코", "title": "이달의 코스트코 스페셜 할인(Executive) 전단지", "details": "https://www.costco.co.kr/offers", "category": "대형마트 통합"},
            {"target": "스타필드", "title": "스타필드 브랜드 팝업스토어 & 주말 컬처 스페셜", "details": "https://www.starfield.co.kr/", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "현대백화점", "title": "더현대 핫플 팝업스토어 & H.Point 사은 행사", "details": "https://www.ehyundai.com/", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "롯데백화점", "title": "롯데백화점 우수고객(MVG) 혜택 & 정기세일 행사", "details": "https://www.lotteshopping.com", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "신세계백화점", "title": "신세계 리워드(신백) 프로모션 & 단독 브랜드 팝업", "details": "https://www.shinsegae.com", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "롯데프리미엄아울렛", "title": "메가세일 & 주말 나들이 가족단위 체험형 팝업", "details": "https://www.lotteshopping.com", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "신세계사이먼프리미엄아울렛", "title": "신세계사이먼 슈퍼세일 & 해외 명품 패밀리세일", "details": "https://www.premiumoutlets.co.kr", "category": "백화점 및 프리미엄 아울렛"},
            {"target": "현대프리미엄아울렛", "title": "현대아울렛 슈퍼위켄드 & 타임세일 파격 할인", "details": "https://www.ehyundai.com/newPortal/outlet/main.do", "category": "백화점 및 프리미엄 아울렛"},
            
            # 의류 / 영화관
            {"target": "유니클로", "title": "유니클로 감사제 & 기간 한정 가격인하(세일)", "details": "https://www.uniqlo.com/kr/ko/", "category": "여가 및 쇼핑 혜택"},
            {"target": "탑텐", "title": "탑텐 텐텐데이 & 행복제 1+1 폭탄 세일", "details": "https://search.naver.com/search.naver?query=%ED%83%9F%ED%85%90", "category": "여가 및 쇼핑 혜택"},
            {"target": "메가박스", "title": "메가박스 빵원티켓 & 오리지널 티켓 증정 이벤트", "details": "https://www.megabox.co.kr/event", "category": "여가 및 쇼핑 혜택"},
            {"target": "CGV", "title": "CGV 스피드쿠폰 & IMAX 스페셜 포스터 굿즈 혜택", "details": "https://www.cgv.co.kr/culture-event/event/defaultNew.aspx", "category": "여가 및 쇼핑 혜택"},
            {"target": "롯데시네마", "title": "롯데시네마 싸다구 예매 & 콤보 선착순 할인", "details": "https://www.lottecinema.co.kr/NLCHS/Event", "category": "여가 및 쇼핑 혜택"},
            
            # 통신사 / 금융
            {"target": "SKT T데이", "title": "매주 수요일 SKT T Day 파격 멤버십 제휴 할인", "details": "https://sktmembership.tworld.co.kr", "category": "통신사 멤버십 혜택"},
            {"target": "KT 달달혜택", "title": "매월 15일경 KT 달달혜택(달달초이스) 혜택 오픈", "details": "https://membership.kt.com/discount/partner/PartnerList.do", "category": "통신사 멤버십 혜택"},
            {"target": "유플투쁠", "title": "매월 2~3째주 LG U+ 유플투쁠 초특가 제휴 할인", "details": "https://www.lguplus.com", "category": "통신사 멤버십 혜택"},
            {"target": "토스", "title": "토스페이 결제 캐시백 & 랜덤 브랜드 혜택 모아보기", "details": "https://toss.im/notice", "category": "금융 및 앱테크"},
            {"target": "네이버페이", "title": "네이버플러스 멤버십 데이 & 현장결제 포인트 뽑기", "details": "https://pay.naver.com", "category": "금융 및 앱테크"},
            {"target": "카카오페이", "title": "카카오페이 결제 리워드 & 페이포인트 적립 찬스", "details": "https://pay.kakao.com", "category": "금융 및 앱테크"},
            
            # 핫딜 커뮤니티 (FMKorea 추가됨)
            {"target": "에펨코리아", "title": "실시간 핫딜 및 초특가 상품 정보(유저 추천)", "details": "https://www.fmkorea.com/hotdeal", "category": "핫딜 커뮤니티"},

            # --- 신규 검증 브랜드 추가 ---
            # 외식 / 패스트푸드 / 피자 / 치킨 / 한식
            {"target": "서브웨이", "title": "이달의 썹프라이즈 & 앱 전용 쿠폰 혜택", "details": "https://www.subway.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노브랜드버거", "title": "NBB 앱 쿠폰 & 신메뉴 세트업 프로모션", "details": "https://search.naver.com/search.naver?query=%EB%85%B8%EB%B8%8C%EB%9E%99%EB%93%9C%EB%B2%84%EA%B1%B0", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "프랭크버거", "title": "이달의 경품 이벤트 & 수제버거 할인 혜택", "details": "https://www.frankburger.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "60계치킨", "title": "자사앱 퀴즈/리뷰 이벤트 & 포장 할인", "details": "https://www.60chicken.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "노랑통닭", "title": "신메뉴 출시기념 할인 & 배달앱 제휴 쿠폰", "details": "https://search.naver.com/search.naver?query=%EB%85%B8%EB%9E%9B%ED%86%B5%EB%8B%AD", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "피자알볼로", "title": "방문포장 할인 & 이달의 멤버십 혜택", "details": "https://www.pizzaalvolo.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "7번가피자", "title": "수/목요일 방문포장 최대 40% 할인 혜택", "details": "https://www.7thpizza.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "동대문엽기떡볶이", "title": "엽떡앱 주문 시 배달/포장 3,000원 상시 할인", "details": "https://www.yupdduk.com", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "한솥도시락", "title": "1월/8월 한솥 매일할인 & 요일별 특가 프로모션", "details": "https://www.hsd.co.kr/event/event_list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "두끼", "title": "이달의 황금레시피 콜라보 & 무한리필 혜택", "details": "https://www.dookki.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "역전할머니맥주", "title": "시즌 신메뉴 프로모션 & 모바일 상품권 이벤트", "details": "https://search.naver.com/search.naver?query=%EC%97%AD%EC%A0%84%ED%95%A0%EB%A8%B8%EB%8B%80%EB%A7%A5%EC%A3%BC", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "본죽", "title": "본오더 앱 전용 3,000원 할인 & 페이백 프로모션", "details": "https://www.bonif.co.kr/event/list", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "신전떡볶이", "title": "신전 앱 첫 구매 쿠폰 & 모바일 상품권 이벤트", "details": "http://www.sinjeon.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "홍콩반점0410", "title": "짜장면데이/단무지데이 파격 할인 프로모션", "details": "https://search.naver.com/search.naver?query=%ED%99%8D%EC%BD%A9%EB%B0%98%EC%A0%900410", "category": "외식/패스트푸드 및 피자/치킨"},
            {"target": "원할머니보쌈", "title": "수요일 방문포장 할인 & 팩 할인 혜택", "details": "https://bossam.co.kr", "category": "외식/패스트푸드 및 피자/치킨"},

            # 카페 / 베이커리 / 디저트
            {"target": "더벤티", "title": "더벤티데이(매월 20일) & 신메뉴 할인 쿠폰", "details": "https://www.theventi.co.kr/new2022/news/event.html", "category": "카페 및 베이커리/디저트"},
            {"target": "공차", "title": "T멤버십 혜택 & 공차 스탬프 트리플 적립", "details": "https://www.gong-cha.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "할리스", "title": "할리스 레드데이 & 멤버십 프리쿠폰 증정", "details": "https://www.hollys.co.kr/news/event/list.do", "category": "카페 및 베이커리/디저트"},
            {"target": "던킨", "title": "던킨 도너츠 팩 할인 & 해피오더 픽업 혜택", "details": "https://www.dunkindonuts.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "크리스피크림도넛", "title": "매월 1, 3번째 수요일 오리지널 1+1 & 롯데잇츠 쿠폰", "details": "https://www.lotteeatz.com", "category": "카페 및 베이커리/디저트"},
            {"target": "요아정", "title": "요아정 앱 첫 구매 할인 & 이달의 토핑 조합 혜택", "details": "https://www.yoajung.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "설빙", "title": "시즌 한정 생과일 빙수 할인 & 기프티콘 프로모션", "details": "https://sulbing.com", "category": "카페 및 베이커리/디저트"},
            {"target": "폴바셋", "title": "폴바셋 소식지 & 멤버십 크라운 적립 쿠폰", "details": "https://www.baristapaulbassett.co.kr", "category": "카페 및 베이커리/디저트"},
            {"target": "아티제", "title": "클럽 아티제 페이코 혜택 & 1+1 음료 쿠폰", "details": "https://www.cafeartisee.com", "category": "카페 및 베이커리/디저트"},

            # 대형마트 / SSM / 쇼핑 / 패션
            {"target": "롯데마트", "title": "롯데마트 전단행사 & 주말 파격 특가 전단지", "details": "https://www.lottemart.com", "category": "대형마트 통합"},
            {"target": "GS더프레시", "title": "GS수퍼 갓세일 & 매주 수요일 오프라인 파격 세일", "details": "https://www.gsretail.com", "category": "대형마트 통합"},
            {"target": "이마트에브리데이", "title": "에브리데이 전단 특가 & 쓱데이 연계 할인", "details": "https://www.emarteveryday.co.kr", "category": "대형마트 통합"},
            {"target": "무인양품", "title": "무지위크(MUJI WEEK) 전 품목 10% 회원 할인", "details": "https://www.muji.kr", "category": "여가 및 쇼핑 혜택"},
            {"target": "모던하우스", "title": "모던하우스 브랜드데이 20% 세일 & 리빙 특가", "details": "https://search.naver.com/search.naver?query=%EB%AA%A8%EB%8D%98%ED%95%98%EC%9A%B0%EC%8A%A4", "category": "여가 및 쇼핑 혜택"},
            {"target": "아트박스", "title": "아트박스 멤버십데이 & 신학기/시즌 세일", "details": "https://www.poom.co.kr", "category": "여가 및 쇼핑 혜택"},
            {"target": "스파오", "title": "스파오 릴레이 세일 & 쿨테크/발열내의 파격 할인", "details": "https://spao.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "ABC마트", "title": "ABC마트 결산 세일 & 한가위/설날 파격 세일", "details": "https://abcmart.a-rt.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "무신사스탠다드", "title": "오프라인 매장 전용 앱 쿠폰 & 무진장 세일", "details": "https://www.musinsa.com", "category": "여가 및 쇼핑 혜택"},

            # 테마파크 / 모빌리티 / 주유
            {"target": "롯데월드", "title": "통신사/카드사 50% 할인 & 이달의 생일/우대 혜택", "details": "https://adventure.lotteworld.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "에버랜드", "title": "제휴카드 스마트예약 할인 & 이달의 프로모션", "details": "https://www.everland.com", "category": "여가 및 쇼핑 혜택"},
            {"target": "쏘카", "title": "내 주변 쏘카존 부름 무료 & 주말 대여료 폭탄 할인", "details": "https://www.socar.kr", "category": "여가 및 쇼핑 혜택"},
            {"target": "GS칼텍스", "title": "에너지플러스 앱 주유 3,000원 할인 & 세차권 쿠폰", "details": "https://www.gscaltex.com", "category": "여가 및 쇼핑 혜택"},

            # 핫딜 커뮤니티
            {"target": "뽐뿌", "title": "뽐뿌 핫딜 게시판 최신 실시간 인기 핫딜", "details": "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu", "category": "핫딜 커뮤니티"},
            {"target": "퀘이사존", "title": "퀘이사존 지름/알뜰정보 실시간 핫딜", "details": "https://quasarzone.com/bbs/qb_saleinfo", "category": "핫딜 커뮤니티"},
            {"target": "어미새", "title": "패션 및 오프라인 쇼핑 실시간 핫딜 정보", "details": "https://eomisae.co.kr", "category": "핫딜 커뮤니티"},
            {"target": "쿨엔조이", "title": "쿨엔조이 알뜰구매 게시판 최신 핫딜", "details": "https://coolenjoy.net/bbs/jirum", "category": "핫딜 커뮤니티"}
        ]
        
        # 동시성(Thread)을 이용해 50개 업체의 최신 뉴스를 1~2초만에 긁어와 병합
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_item = {executor.submit(self._fetch_news_headline, item["target"]): item for item in base_data}
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                new_headline = future.result()
                if new_headline:
                    item["title"] = item["title"] + new_headline

        return base_data
