# OZ Report Generator - SoT (Single Source of Truth) Index

이 디렉터리는 **OZ Report Generator** 프로젝트의 **단일 진실 공급원(SoT)**입니다.
모든 구현과 AI 에이전트의 작업은 이 문서를 최우선으로 준수해야 합니다.

## 🚨 최우선 원칙 (Strict Rules)
1. **OZR 파일 구조 100% 동기화**: 자동 생성된 OZR 파일은 반드시 수작업 파일(예: `PLA0501_R25.ozr`)의 XML 트리 구조와 태그 순서를 완벽히 재현해야 합니다.
2. **동적 파싱 (하드코딩 금지)**: 특정 엑셀 양식의 Row 번호(예: 10번 줄)를 하드코딩하지 않습니다. 데이터 행의 가로폭과 테두리 정렬을 동적으로 분석하여 `PageHeaderBand`, `DataBand`, `PageFooterBand`를 영리하게 분리해야 합니다.
3. **불필요한 반복 빈칸 무시**: 데이터 템플릿(Grid)이 여러 줄 비워져 있더라도, 디자인 유지를 위한 반복 행은 스킵하고 실제 데이터 바인딩 패턴(`<TR_VIEW:...>`)이 있는 첫 행만 렌더링에 사용합니다.

## 문서 분류 (Categories)
- `00_SOT/` : 제품 범위, 제약 사항, 코딩 원칙 및 표준 협업/문서화 규칙 (`product-scope.md`, `collaboration-rules.md`)
- `90_Worklog/` : 일자별 작업 일지 (`WORK_HISTORY_YYYYMMDD.md`)
