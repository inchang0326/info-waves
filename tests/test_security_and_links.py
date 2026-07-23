import os
import pytest
from services.ui_utils import generate_card_html, generate_mini_popup_html
from services.location_service import LocationService

def test_gitignore_security():
    """프로젝트 루트에 .gitignore가 존재하며 중요 환경변수 및 로그 파일이 제대로 제외되었는지 검증합니다."""
    gitignore_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".gitignore")
    assert os.path.exists(gitignore_path), ".gitignore file must exist"
    
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert ".env" in content
    assert "logs/" in content or "*.log" in content
    assert ".secrets.toml" in content

def test_card_links_target_blank_and_escaping():
    """업체별 링크 카드 생성 시 target='_blank' 및 rel='noopener noreferrer' 속성 적용 및 XSS 이스케이핑을 검증합니다."""
    brand = "<script>alert(1)</script>버거킹"
    title = "<b>행사</b> 와퍼"
    link = "https://www.burgerking.co.kr/#/event"
    
    html_out = generate_card_html(brand, title, link)
    assert 'target="_blank"' in html_out
    assert 'rel="noopener noreferrer"' in html_out
    assert '<script>' not in html_out
    assert '&lt;script&gt;' in html_out

def test_popup_links_target_blank_and_escaping():
    """지도 팝업 생성 시 target='_blank' 및 rel='noopener noreferrer' 속성 적용을 검증합니다."""
    popup_out = generate_mini_popup_html("스타벅스", "행사", "https://www.starbucks.co.kr")
    assert 'target="_blank"' in popup_out
    assert 'rel="noopener noreferrer"' in popup_out

def test_search_place_taeseongro():
    """태성로 107 위치 검색 시 정합성 있는 위경도 좌표(lat, lon)가 정상 반환되는지 검증합니다."""
    ls = LocationService()
    lat, lon = ls.search_place("태성로 107")
    assert lat is not None and lon is not None
    assert 33.0 <= lat <= 39.0
    assert 124.0 <= lon <= 132.0
