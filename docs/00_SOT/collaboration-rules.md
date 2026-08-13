# Standard Collaboration & Workflow Rules

## 1. 기본 원칙
- **코드 수정과 SoT 문서는 원자적 단위(Single Unit of Work)**로 함께 관리됩니다.
- OZR 생성 파이프라인이나 엑셀 파싱 로직(Heuristic)을 개선하거나 변경할 때는 반드시 `docs/00_SOT/product-scope.md` 등의 문서를 동기화하여 변경 사항을 문서에 반영해야 합니다.

## 2. 작업 시작 트리거 ("여기서 할게")
- 새로운 작업 세션 또는 타 PC에서 작업을 재개할 때는 가장 먼저 다음 파일들을 읽어 맥락을 재구성합니다:
  - `llms.txt` (핵심 진입점)
  - `docs/INDEX.md` (구조 파악)
  - `docs/90_Worklog/` 내 가장 최근의 작업 일지

## 3. 작업 완료 트리거 ("pr 생성해" / "마무리 해")
- 해당 세션의 주요 변경 사항(예: 파싱 알고리즘 개선, 새로운 OZR 태그 지원 등)을 `docs/90_Worklog/WORK_HISTORY_YYYYMMDD.md`에 상세히 기록합니다.
- 작성된 기록은 추후 다른 AI 에이전트나 개발자가 맥락을 빠르게 파악할 수 있는 핵심 히스토리가 됩니다.
- 코드와 문서를 모두 커밋(Commit)하고 푸시(Push)하여 형상 관리에 반영합니다.
