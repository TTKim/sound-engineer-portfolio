# Portfolio Design Research (2026-03-08)

## Goal
현재 포트폴리오의 장점(작업 아카이브/필터 구조)은 유지하면서,
`priority` 기반 노출을 시각적으로 더 설득력 있게 전달하는 방향을 찾는다.

## What can be improved from current page
- 카테고리 카드 썸네일이 완전 랜덤처럼 보여서, 중요한 레퍼런스가 기억에 덜 남는다.
- 카드가 모두 비슷한 시각 무게를 가져서 "무엇을 먼저 봐야 하는지"가 약하다.
- 모바일에서 카드 스캔 속도는 좋지만, 상단에서 핵심 큐레이션 메시지가 약하다.

## Research-backed principles
1. **Strong visual hierarchy first**
- NN/g는 크기, 대비, 간격 등 시각 변수로 우선순위를 명확히 전달해야 한다고 제시한다.
- 적용: `Priority Spotlight`를 첫 섹션으로 올리고, 우선순위가 높은 앨범은 큰 카드/강한 대비로 노출.
- Source: https://www.nngroup.com/articles/principles-visual-design/

2. **Accessibility baseline is non-negotiable**
- WCAG 2.2 Quickref 기준(대비, 키보드 접근, 모션/자동재생 관련 기준)을 디자인 초안 단계에서 체크해야 한다.
- 적용: 버튼/텍스트 대비 강화, 포커스 가능한 인터랙션 유지, 모션 축소 환경 대응.
- Source: https://www.w3.org/WAI/WCAG22/quickref/

3. **Performance keeps aesthetics usable**
- web.dev는 LCP를 주요 UX 지표로 보고, 핵심 리소스의 우선 로딩과 렌더 차단 최소화를 강조한다.
- 적용: 상단 히어로/스포트라이트 이미지는 lazy 전략을 유지하되, 첫 화면 우선 노출 카드 수를 제한.
- Source: https://web.dev/articles/optimize-lcp

4. **Respect motion preferences**
- MDN의 `prefers-reduced-motion`은 강한 모션/패럴랙스 사용 시 필수 가드레일.
- 적용: 시안에서 reduced-motion 미디어쿼리로 transition 최소화.
- Source: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

## Visual references (style direction)
- Awwwards music/portfolio 계열 레퍼런스에서 공통적으로 "큰 히어로 + 강한 타이포 + 큐레이션 섹션" 구조가 많다.
- Source: https://www.awwwards.com/websites/music/

## Local mockup created
- File: `design_mockup_priority_v2.html`
- Intent:
  - `priority`를 설명 가능한 방식으로 상단 고정 노출
  - 가중 랜덤 썸네일 월(완전 랜덤 아님)
  - 기존 아카이브 데이터(`Portfolio_list.csv`)를 직접 읽어서 즉시 검토 가능
