# Product Scope & Core Constraints (OZ Report Generator)

## 1. 개요 (Overview)
- **프로젝트명**: OZ Report Generator (Excel to OZR/ODI Converter)
- **목적**: 엑셀로 작성된 설계 템플릿과 데이터 바인딩 포맷을 읽어, OZ Report 디자이너에서 수작업한 것과 완벽히 동일한 결과물(`.ozr`, `.odi`)을 자동으로 변환 및 생성하는 백엔드/프론트엔드 시스템.

## 2. 🚨 절대 준수 제약사항 (Critical Constraints)
1. **OZR XML 태그 및 구조 완벽 재현**:
   - 백엔드의 `ozr_generator.py`는 사람(Human)이 디자이너 툴에서 만든 파일(예: `PLA0501_R25.ozr`)의 태그 순서를 100% 동일하게 맞춰야 합니다.
   - 필수 메타데이터 태그의 순서 (`VERSION` -> `BASICLABEL` -> `DEFAULTLABEL` -> `EVENT` -> `REPORTINFO` -> `OZPARAMETERTOOLBARS` -> `OZFONTDESC` -> `OZODILIST` -> `OZGRIDINFO` -> `OZFORMIDINFO`)를 반드시 준수합니다.
2. **동적 밴드(Band) 분리 알고리즘 유지**:
   - `xlsx_parser.py`는 절대 "Row 10"과 같이 고정된 숫자로 헤더를 찾지 않습니다.
   - 데이터 패턴(`<...:...>`)이 있는 Row를 기준으로, 위로 올라가며 가로폭 정렬이 일치하는 행을 `DataBand`의 `TableTitle`로, 형태가 무너지는 상단 병합 행들을 `PageHeaderBand`로 영리하게 분리해야 합니다.
3. **가로 모드(Landscape) 지원 유지**:
   - 와이드 엑셀 양식 처리를 위해 `OnStartUp` 이벤트 스크립트(`SetReportOption("viewer.paper_orientation","horizontal");`)가 항상 포함되어야 합니다.

## 3. 주요 기능 (Key Features)
- 엑셀 양식을 OZ Report 3단 구조(페이지 헤더, 데이터 반복 밴드, 페이지 풋터)로 자동 분리 및 변환.
- 시각적 디자인 유지를 위해 엑셀에 그려진 불필요한 반복 빈칸 표 자동 무시.
- 변환된 OZR 텍스트 구조 디버깅 및 분석 툴 제공 (`dump_ozr.py`, `compare_text.py` 등).
