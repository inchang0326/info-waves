# 프로젝트 규칙 (Project Rules)

## 지도 조작 및 상태 관리 절대 원칙 (Map Interaction State Management)
이 규칙은 `app.py`의 `st_folium` 지도 조작 로직이 훼손되거나 튕김(Snap-back) 버그가 재발하는 것을 막기 위한 필수 가이드라인입니다. 모든 에이전트(AI)와 개발자는 `app.py`를 수정할 때 다음 원칙을 반드시 지켜야 합니다.

1. **과거 클릭 캐시(Stale Click Event) 무시 로직 유지**
   - `st_folium`은 컴포넌트가 다시 렌더링될 때마다 마지막으로 클릭된 좌표(`last_clicked`)를 계속해서 반환하는 특성이 있습니다. 
   - 이를 방어하기 위해 `_last_processed_click` 세션 상태를 사용하여, 이전 클릭 좌표와 일치하면 무시하는 필터링 로직이 구현되어 있습니다. 
   - **절대 금지:** 장소 검색(`location_service.search_place`) 등 지도 위치를 코드로 이동시킬 때, `st.session_state["_last_processed_click"] = None` 과 같이 이 캐시 방어 변수를 초기화하지 마세요. 초기화할 경우 지도가 다시 옛날 클릭 위치로 튕겨버리는 치명적인 버그가 재발합니다.

2. **동적 뷰포트 아키텍처 훼손 금지**
   - 지도를 초기화하는 `folium.Map()` 객체는 항상 최초 1회 생성용 고정 값만 가져야 합니다.
   - 지도 중심 이동과 줌은 반드시 `st_folium(center=..., zoom=...)` 파라미터를 통해서만 동적으로 주입되어야 합니다. HTML 재생성으로 인한 깜빡임을 막는 핵심 구조입니다.

3. **위젯 상태 역방향 할당 금지**
   - `st.slider`와 같이 고유의 `key`를 가진 Streamlit 위젯은, 해당 위젯이 코드 상에서 렌더링된 **이후**에 코드 하단에서 그 상태값을 강제로 덮어쓰기(`st.session_state["radius_slider"] = ...`) 하려고 하면 `StreamlitAPIException`을 발생시키고 앱을 중단시킵니다.
   - 뷰 업데이트 사이클(rerun)을 꼬이게 하는 위젯 상태 강제 덮어쓰기를 지양하고, 사용자가 선택한 반경 설정 등은 검색이나 이동 시에도 그대로 유지(Persist)되도록 하세요.

4. **지도 조작 로직 Read Only 원칙 (Map Interaction Lock)**
   - 현 시점 기준으로 `app.py`에 구현된 지도 조작 로직(커맨드 패턴 기반 카메라 이동, 동적 key 관리 등)은 안정성 검증이 완료된 최종 형태입니다.
   - UI 개선이나 새로운 기능 추가 등의 어떠한 명분으로도 지도 상태 관리 로직(`map_lat`, `map_lon`, `map_center`, `map_cmd_center`, `map_cmd_zoom`) 및 `st_folium` 컴포넌트 호출부를 수정하는 것을 **절대 금지(Read Only)**합니다.
   - 무분별한 수정으로 인한 사이드 이펙트(Side-effects)를 원천 차단하기 위해, 해당 부분은 영구적인 잠금(Lock) 상태로 취급하십시오.
