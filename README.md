# 📍 Geo-Alert Tracker (Info Waves)

**Info Waves**는 위치 기반 프랜차이즈 혜택 및 실시간 핫딜 정보를 수집·역매핑하여 제공하는 종합 혜택 탐색 웹 애플리케이션입니다.

---

## 🎯 프로젝트 목표 및 목적

- **실시간 혜택 정보 통합 수집**: 편의점, 카페, 패스트푸드, 피자, 치킨, H&B, 백화점, 아울렛, 영화관 등 국내 50여 개 주요 프랜차이즈의 공식 이벤트 및 프로모션 정보를 실시간 수집합니다.
- **위치 기반 맞춤 매핑**: 사용자의 현재 GPS 좌표 또는 지정한 위치(장소/역/지번)를 중심으로 설정된 반경(0.5km ~ 10km) 내 매장을 자동 조회하고, 해당 매장에서 이용 가능한 혜택을 브랜드별 그룹화 형태로 제공합니다.
- **신뢰성 높은 공식 데이터 제공**: 블로그나 낚시성 뉴스 대신 공식 브랜드 홈페이지 및 프로모션 랜딩 페이지 링크를 매핑하여 유효한 혜택 정보만 전달합니다.

---

## 🌐 도메인 영역

본 프로젝트는 **위치 기반 혜택 애그리게이터 (Geospatial Deal & Discount Aggregator)** 도메인에 속합니다.

- **위치 정보 처리 (Geospatial Processing)**: GPS / IP 기반 좌표 수집, OpenStreetMap 역지오코딩(Reverse Geocoding), 카카오 맵 지점 검색, Haversine 반경 거리 계산.
- **웹 데이터 수집 (Web Scraping & Aggregation)**: 공식 웹사이트 혜택 파싱, Google News RSS 기반 실시간 핫트렌드 결합, 핫딜 커뮤니티(루리웹, 에펨코리아 등) 수집.
- **데이터 시각화 및 UI/UX**: Streamlit 기반 지도(Folium) 및 리스트 인터랙티브 뷰 제공.

---

## 📂 디렉토리 구조

```text
info_waves/
├── app.py                     # Streamlit 기반 메인 웹 애플리케이션 (UI/UX, 지도 렌더링, 이벤트 컨트롤)
├── main.py                    # 혜택 수집 및 오프라인 매장 역매핑 파이프라인 오케스트레이터
├── config.py                  # Pydantic Settings 기반 환경 변수 및 시스템 설정 관리
├── requirements.txt           # 프로젝트 의존성 라이브러리 목록
├── .env.example               # 환경 변수 설정 예시 파일
├── README.md                  # 프로젝트 설명 및 사용 가이드
├── data/
│   └── location_cache.sqlite  # 카카오 맵 매장 검색 결과 영속성 캐시 DB (SQLite WAL)
├── services/
│   ├── __init__.py
│   ├── scraper_service.py     # 멀티스레드 기반 하이브리드 파싱 엔진 (공식 사이트 + RSS + 커뮤니티)
│   ├── location_service.py    # IP/GPS 위치 추적, 역지오코딩, 카카오 맵 지점 검색 및 2단계 캐싱
│   ├── ui_utils.py            # 브랜드 로고 CDN/SVG 처리, 혜택 카드 HTML, 맵 팝업, 클립보드 스크립트
│   ├── notifier_service.py    # Console 및 Discord Webhook 알림 발송 서비스
│   └── logger_utils.py        # 표준 로깅 유틸리티
├── ui_components/             # Streamlit Custom Components (HTML5/JS)
│   ├── device_location/       # 브라우저 HTML5 Geolocation 사용자 위치 자동 수집 컴포넌트
│   └── kakao_search/          # 지도 상단 Floating 검색창 및 내 위치 바로가기 컴포넌트
└── tests/                     # pytest 기반 테스트 스위트 (단위/통합/성능/스트레스 테스트)
    ├── test_app_execution.py
    ├── test_location_service.py
    ├── test_main_pipeline.py
    ├── test_performance_and_parity.py
    ├── test_scraper_service.py
    ├── test_stress.py
    ├── test_ui_refinements.py
    ├── test_ui_utils.py
    └── test_usecases.py
```

---

## 🚀 주요 기능

### 1. 하이브리드 데이터 파싱 엔진 (`HybridOfficialScraper`)
- 50여 개 프랜차이즈 브랜드의 공식 혜택 랜딩 페이지(`HTTP 200 OK` 검증 완료) 데이터 세트 보유.
- `ThreadPoolExecutor`를 통한 비동기 병렬 처리(20개 스레드)로 Google News RSS 키워드 검색을 수행하여 실시간 신규 이벤트 헤드라인(`[신규]`)을 1~2초 내에 병합.
- 루리웹, 에펨코리아 등 커뮤니티 핫딜 정보 수집 지원.

### 2. 위치 기반 주변 매장 역매핑 (`LocationService`)
- HTML5 Geolocation API를 통한 브라우저 실제 좌표 수집, 실패 시 IP 기반 위치(`ip-api.com`) 및 사용자 직접 장소/역명/주소 검색 기능 제공.
- OpenStreetMap Nominatim API 기반 행정동 역지오코딩.
- 지정된 반경(0.5km ~ 10km) 내 브랜드 매장을 조회하고, Haversine 공식을 적용하여 거리순으로 정렬.
- SQLite WAL 모드 영속 캐시(`data/location_cache.sqlite`) 및 Python `lru_cache` 2단계 캐싱으로 반복 API 호출을 방지하고 응답 속도 최적화.

### 3. 인터랙티브 웹 UI (`app.py`, Folium)
- **이중 뷰 체계**: '내 주변 맞춤 혜택' (지도 + 매장 매핑 리스트) 및 '전국구 핫딜' (카테고리별 카드 뷰) 제공.
- **브랜드 단위 그룹화 (Grouping UI)**: 혜택별 주변 매장 지점을 Expander 구조로 묶어 직관적인 오프라인 매칭 정보 표시.
- **다크 / 라이트 테마**: Pure JavaScript 기반의 클라이언트 사이드 테마 전환 (Streamlit 재실행 없이 변경).
- **주소 복사 유틸리티**: 매칭된 오프라인 매장의 도로명/지번 주소를 원클릭으로 클립보드에 복사.

### 4. 알림 서비스 (`NotifierService`)
- 혜택 정보 발신을 위한 Console 알림 및 Discord Webhook 연동 구조 지원.

---

## 🛠 사용 기술 및 라이브러리

- **언어 및 런타임**: Python 3.10+
- **웹 프레임워크 / UI**: Streamlit `1.33.0`, Folium `0.15.1`, streamlit-folium `0.21.0`, HTML5 / CSS3 / JavaScript (Pretendard 폰트, Custom Streamlit Components)
- **스크래핑 & HTTP**: BeautifulSoup4 `4.12.3`, requests `2.31.0`, Playwright `1.42.0`, lxml `5.1.0`
- **위치 API & 지오패셜**: Kakao Map Search API (`search.map.kakao.com`), OpenStreetMap Nominatim, Haversine Distance Formula
- **데이터 캐싱 & 설정**: SQLite3 (WAL 모드), Python `functools.lru_cache`, Pydantic `2.6.4`, Pydantic-Settings `2.2.1`
- **동시성 & 테스트**: `concurrent.futures.ThreadPoolExecutor`, APScheduler `3.10.4`, pytest `8.1.1`

---

## ⚠️ 제약 및 제한사항

1. **외부 지도 API 엔드포인트 의존성**:
   - `search.map.kakao.com` 웹 검색 엔드포인트를 사용하므로, 해당 서비스의 네트워크 상태 또는 트래픽 제약(Rate Limit)에 영향을 받을 수 있습니다.
2. **역지오코딩 호출 제한**:
   - OpenStreetMap Nominatim API 호출 시 서버 정책에 따라 딜레이(타임아웃 5초) 및 헤더 설정이 적용되며, 1차적으로 LRU 메모리 캐시를 통해 중복 요청을 방지합니다.
3. **공식 URL 유지보수 필요성**:
   - 브랜드 공식 홈페이지의 URL 구조가 개편되거나 폐쇄되는 경우, `base_data` 내부 링크 수동 업데이트가 필요합니다.
4. **브라우저 위치 권한 요구사항**:
   - HTML5 Geolocation API는 보안 컨텍스트(HTTPS 또는 localhost)에서 정상 가동하며, 사용자 권한 거부 시 IP 위치 추적 또는 기본 좌표가 적용됩니다.
5. **서버 동시성 자원 제약**:
   - 멀티스레딩 파싱 및 지점 역매핑 시 스레드 풀(20~30 worker)을 활용하므로, 호스트 시스템의 CPU 및 네트워크 대역폭에 의존합니다.
