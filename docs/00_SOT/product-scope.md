# Product Scope & Core Constraints (OZ Report Generator)

## 1. 개요 (Overview)
- **프로젝트명**: OZ Report Generator (Excel to OZR/ODI Converter)
- **목적**: 엑셀로 작성된 설계 템플릿과 데이터 바인딩 포맷을 읽어, OZ Report 디자이너에서 수작업한 것과 완벽히 동일한 결과물(`.ozr`, `.odi`)을 자동으로 변환 및 생성하는 백엔드/프론트엔드 시스템.

## 2. 🚨 절대 준수 제약사항 및 핵심 알고리즘 (Critical Rules)

### ① OZR XML 태그 및 구조 완벽 재현 (100% Parity)
- 백엔드의 `ozr_generator.py`는 수작업 원본(`PLA0501_R25.ozr`)의 XML 트리 구조와 태그 순서를 100% 유지해야 합니다.
- **루트 태그 필수 순서**: 
  `VERSION` ➔ `BASICLABEL` ➔ `DEFAULTLABEL` ➔ `EVENT` ➔ `REPORTINFO` ➔ `OZPARAMETERTOOLBARS` ➔ `OZFONTDESC` ➔ `OZODILIST` ➔ `OZGRIDINFO` ➔ `OZFORMIDINFO`
- **가로 모드(Landscape) 스크립트 필수 삽입**:
  `<EVENT NAME="OnStartUp" EVENTTYPE="Any" EVENTVALUE='SetReportOption("viewer.paper_orientation","horizontal");'/>` 태그를 항상 포함합니다.

### ② 지능형 3단 밴드 동적 파싱 알고리즘 (`xlsx_parser.py`)
- **절대 금지**: "Row 10이 헤더다"와 같은 하드코딩된 행 번호 지정을 절대 금지합니다. 어떤 엑셀 템플릿이 들어와도 아래 세로선 정렬 추적 알고리즘으로 동적 처리해야 합니다.
- **기준점(Data Row Anchor)**: `<...:...>` 데이터 바인딩 패턴이 있는 첫 줄을 `data_row_num`으로 탐색.
- **상단 추적 (Page Header vs TableTitle)**:
  - `data_row_num`의 가로 경계선(Left & Width Bounds)을 추출.
  - 위로 올라가며 가로선 일치율(Match Ratio)이 50% 이상인 1~2줄만 `DataBand`의 `TableTitle`로 분리.
  - 일치율이 50% 미만인 넓은 병합 셀(프로젝트 정보, 계약선, 결재란 등)은 모두 `PageHeaderBand`의 정적 라벨(`OZTABLELABEL`)로 자동 전송.
- **하단 추적 (반복 빈칸 스킵 & Page Footer)**:
  - `data_row_num` 아래로 내려가며 가로선 일치율 50% 이상인 연속된 반복 빈칸 표 행(예: 13~30줄)은 **모두 무시(Skip)**.
  - 가로선 일치율이 50% 미만으로 무너지는 지점(비고란, 서명란 등)부터 `footer_start`로 분류하여 `PageFooterBand`로 배치.
  - **Y좌표 보정**: `PageFooterBand` 라벨의 `top` 좌표는 `footer_start - 1` 높이를 차감하여 밴드 내부에서 `top=0`부터 정렬되도록 보정.

### ③ 에이전트 작업 영속성 (Agent Rules)
- **작업 시작 ("여기서 할게")**: `llms.txt`, `docs/INDEX.md`, `docs/90_Worklog/` 최신 일지 수독 후 맥락 파악.
- **작업 종료 ("마무리 해" / "pr 생성해")**: `docs/90_Worklog/WORK_HISTORY_YYYYMMDD.md` 작성, feature 브랜치 커밋/푸시, GitHub API로 PR 생성 및 `main` 자동 병합.

## 3. 주요 기능 (Key Features)
- 엑셀 양식을 OZ Report 3단 구조(페이지 헤더, 데이터 반복 밴드, 페이지 풋터)로 자동 분리 및 변환.
- 시각적 디자인 유지를 위해 엑셀에 그려진 불필요한 반복 빈칸 표 자동 무시.
- 변환된 OZR 텍스트 구조 디버깅 및 분석 툴 제공 (`dump_ozr.py`, `compare_text.py` 등).
