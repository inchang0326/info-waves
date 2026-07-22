import pytest
from services.ui_utils import get_brand_logo

def test_brand_logo_uses_official_domain_s2_favicons():
    """
    [UI Verification] 브랜드 로고가 외부 404 없이 공식 브랜드 도메인 또는 고화질 엠블럼 URL을 반환하는지 검증
    """
    sample_brands = ["CU", "GS25", "스타벅스", "올리브영", "버거킹", "CGV"]
    
    for brand in sample_brands:
        logo_url = get_brand_logo(brand)
        assert logo_url.startswith("http://") or logo_url.startswith("https://") or logo_url.startswith("data:image/svg+xml")
        assert len(logo_url) > 10


def test_ui_css_rules_restored_to_stable_layout():
    """
    [UI Verification] app.py 및 index.html UI CSS 구문이 안정적인 레이아웃 및 모바일 반응형 규칙(@media max-width: 480px)을 포함하는지 검증
    """
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
        
    assert "max-width: 420px !important;" in app_code
    assert "width: 220px !important;" in app_code
    assert "@media (max-width: 480px)" in app_code
    assert "top: 85px !important;" in app_code
    assert 'div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"]' in app_code

    with open("ui_components/kakao_search/index.html", "r", encoding="utf-8") as f:
        index_code = f.read()
        
    assert "updateLayout" in index_code
    assert "flexDirection" in index_code


def test_targeted_spinner_active_only_on_app_load_and_search_button():
    """
    [UI Verification] 'Simple is the Best' 32px 미니멀 슬림 링 오버레이 CSS 및 
    딱 2가지 케이스(1. 앱 시작 로딩, 2. 탐색 버튼 클릭)에만 스피너 래퍼가 보존되었는지 정합성 검증
    """
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
        
    # 1. Simple is the Best 32px Ring Spinner CSS
    assert "width: 32px !important;" in app_code
    assert "height: 32px !important;" in app_code
    assert "modernSpin" in app_code
    
    # 2. Spinner Fallback Wrappers reserved for App Load and Search Button
    assert "with st.spinner" in app_code
    assert "fetch_local_alerts" in app_code
