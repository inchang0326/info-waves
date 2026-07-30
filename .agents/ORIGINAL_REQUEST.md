# Original User Request

## 2026-07-30T15:38:33Z

<USER_REQUEST>
거지맵(가성비 식당 맵) 랜딩 시, 거지맵 메인 도메인(`https://xn--v69ak0xskm.com`)으로 이동함과 동시에 해당 식당 주소가 자동으로 기입 및 검색되도록 원인을 분석하고 코드를 수정합니다.

Working directory: /Users/steady/.openclaw/workspace/info_waves
Integrity mode: development

## Requirements

### R1. 거지맵 주소 파라미터 규명
거지맵 웹사이트 혹은 소스코드를 분석하여(필요시 브라우저 에이전트 활용), 외부에서 주소 검색 결과를 띄우기 위해 사용하는 정확한 URL 파라미터 구조(예: `?q=`, `?search=`, 혹은 URL Path 등)를 파악해야 합니다.

### R2. 거지맵 링크(details) 반환 로직 롤백 및 적용
`scraper_service.py` 내 `GuziMapScraper`에서 네이버 플레이스로 넘어가던 로직을 제거하고, R1에서 파악한 거지맵의 검색 URL 구조를 사용하여 식당 주소가 자동으로 주입되도록 수정합니다.

## Acceptance Criteria

### 랜딩 정확성 검증
- [ ] 브라우저에서 수정된 거지맵 링크(`details` URL) 접속 시 메인 페이지가 아닌 해당 주소가 입력된 검색 결과 화면이 정상적으로 나타나야 합니다.
- [ ] `pytest` 테스트 코드 85개가 사이드 이펙트 없이 100% 통과해야 합니다. (특히 거지맵 관련 `test_guzimap_integration.py` 어서션 업데이트 필수)
</USER_REQUEST>
