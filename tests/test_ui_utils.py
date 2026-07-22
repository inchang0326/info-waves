import pytest
from services.ui_utils import (
    get_brand_logo, get_zoom_for_radius,
    generate_card_html, generate_mini_popup_html, format_expander_title
)

def test_get_brand_logo():
    """브랜드 엠블럼 매핑 및 공식 브랜드 도메인/고화질 엠블럼 URL 반환 정합성을 검증합니다."""
    cu_logo = get_brand_logo("CU")
    assert cu_logo.startswith("http://") or cu_logo.startswith("https://") or cu_logo.startswith("data:image/svg+xml")
    assert len(cu_logo) > 10

    seven_eleven_logo = get_brand_logo("세븐일레븐")
    assert seven_eleven_logo.startswith("http://") or seven_eleven_logo.startswith("https://") or seven_eleven_logo.startswith("data:image/svg+xml")

    general_logo = get_brand_logo("알수없는브랜드")
    assert "data:image/svg+xml" in general_logo or "google.com" in general_logo

def test_get_zoom_for_radius():
    """탐색 반경(km)에 따른 Folium 지도 줌 레벨 변환 정합성을 계단식 수치별로 검증합니다."""
    assert get_zoom_for_radius(0.3) == 16
    assert get_zoom_for_radius(0.5) == 16
    assert get_zoom_for_radius(1.0) == 15
    assert get_zoom_for_radius(2.0) == 14
    assert get_zoom_for_radius(3.0) == 13
    assert get_zoom_for_radius(5.0) == 12
    assert get_zoom_for_radius(10.0) == 11

def test_generate_card_html_single():
    """지점 목록 없는 단일 전국구 핫딜 카드 HTML 생성 구조를 원자 단위로 검증합니다."""
    card_html = generate_card_html("버거킹", "와퍼주니어 반값 행사", "https://www.burgerking.co.kr/#/event")
    assert '<div id="c' in card_html
    assert 'class="info-card"' in card_html
    assert '버거킹' in card_html
    assert '와퍼주니어 반값 행사' in card_html
    assert 'https://www.burgerking.co.kr/#/event' in card_html
    assert 'details class="branches-details"' not in card_html # 단일 카드에는 드롭다운 없음

def test_generate_card_html_with_branches():
    """내 주변 지점 목록(branches)이 포함된 오프라인 그룹핑 카드 HTML 생성 및 드롭다운 구조를 검증합니다."""
    branches = [
        {"target": "CU 산본에듀점", "address": "경기도 군포시 산본동 100", "road_address": "산본로 123"},
        {"target": "CU 산본역점", "address": "경기도 군포시 산본동 200", "road_address": "번영로 456"}
    ]
    card_html = generate_card_html("CU", "쓔퍼세일 1+1 혜택", "https://cu.bgfretail.com", branches=branches)
    
    assert 'class="info-card"' in card_html
    assert 'CU' in card_html
    assert 'details class="branches-details"' in card_html # 지점 포함 시 Accordion 생성
    assert 'CU 산본에듀점' in card_html
    assert 'CU 산본역점' in card_html
    assert '산본로 123' in card_html
    assert 'copy-addr-btn' in card_html

def test_generate_mini_popup_html():
    """지도 마커 팝업용 HTML 구조 및 텍스트 렌더링을 검증합니다."""
    popup_html = generate_mini_popup_html("스타벅스", "e-프리퀀시 이벤트", "https://www.starbucks.co.kr")
    assert '스타벅스' in popup_html
    assert 'e-프리퀀시 이벤트' in popup_html
    assert 'https://www.starbucks.co.kr' in popup_html

def test_format_expander_title():
    """카테고리명 정제 및 아이템 수량 포맷팅 타이틀 출력을 검증합니다."""
    assert format_expander_title("편의점 혜택", 5) == "편의점 (5개)"
    assert format_expander_title("외식/패스트푸드 및 피자/치킨", 12) == "패스트푸드 (12개)"
    assert format_expander_title("카페 및 베이커리/디저트", 8) == "카페/디저트 (8개)"
    assert format_expander_title("백화점 및 프리미엄 아울렛", 3) == "백화점/아울렛 (3개)"
