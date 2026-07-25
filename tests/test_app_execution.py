import os
import py_compile
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st

def test_app_compilation_integrity():
    """
    [App Execution] app.py 파일의 파이썬 구문 오류 및 f-string 이스케이프, 문법 정합성 검증
    """
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            compile(f.read(), "app.py", "exec")
    except Exception as e:
        pytest.fail(f"app.py 파이프라인 컴파일 실패: {e}")


def test_app_script_execution_and_rendering():
    """
    [App Execution] Streamlit 세션 환경에서 app.py 스크립트 실행 시 런타임 예외 없이 정상 렌더링되는지 보증
    """
    class SessionMock(dict):
        def __getattr__(self, name):
            if name in self:
                return self[name]
            raise AttributeError(name)
        def __setattr__(self, name, value):
            self[name] = value
        def __delattr__(self, name):
            if name in self:
                del self[name]

    session_mock = SessionMock({
        "map_lat": 37.360657,
        "map_lon": 126.928194,
        "map_key_id": 0,
        "radius_val": 3.0,
        "data_view": "내 주변 맞춤 혜택"
    })
    
    with patch.object(st, "session_state", session_mock), \
         patch("app.get_global_data", return_value={}), \
         patch("services.location_service.LocationService.get_current_location", return_value=(37.360657, 126.928194)), \
         patch("services.location_service.LocationService.get_neighborhood", return_value="산본동"), \
         patch("streamlit_folium.st_folium", return_value={"last_clicked": None}):
        
        # app.py 톱레벨 실행 시 예외 발생 여부 검증
        try:
            app_path = os.path.abspath("app.py")
            with open(app_path, "r", encoding="utf-8") as f:
                code = compile(f.read(), app_path, "exec")
                exec_globals = {"__name__": "__main__", "__file__": app_path}
                exec(code, exec_globals)
        except Exception as e:
            pytest.fail(f"app.py 런타임 실행 중 오류 발생: {e}")
