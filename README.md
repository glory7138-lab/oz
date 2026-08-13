# OZ Report (.ozr / .odi) 자동 생성기

사용자가 엑셀 양식(.xlsx)을 업로드하면, AI API 없이 `openpyxl` 엔진으로 상단(Header), 테이블 데이터(Body), 하단(Footer)을 자동 분석하여 OZ Report 규격에 맞게 `.ozr` 및 `.odi` 파일을 자동 생성하는 웹 애플리케이션입니다.

---

## 📁 프로젝트 파일 구조 (`d:\DEV\oz\`)

```
d:\DEV\oz\
├── backend/
│   ├── main.py              # FastAPI 서버 (포트 8088, SSE 진행상태 스트리밍)
│   ├── xlsx_parser.py       # 엑셀 파서 (Header/Body/Footer 자동 영역 분류)
│   ├── ozr_generator.py     # OZR XML 및 바이너리 생성 엔진 (VERSION 7.0 준수)
│   ├── odi_generator.py     # ODI 더미 파일 생성 엔진 (기존 ODI 복사/참조)
│   ├── file_manager.py      # PLA0501_R 고정 채번 및 파일 저장 관리
│   └── requirements.txt     # Python 패키지 의존성 목록
├── frontend/
│   ├── package.json         # Next.js 프론트엔드 설정 (포트 3088)
│   ├── next.config.js       # 백엔드 API 프록시 (http://localhost:8088)
│   └── app/
│       ├── page.js          # 3단계 플로우 UI (업로드 → 미리보기 → 실시간 생성)
│       ├── layout.js        # 루트 레이아웃
│       └── globals.css      # 프리미엄 다크모드 글래스모피즘 디자인
├── install_deps.bat         # [1단계] 의존성 패키지 전용 설치 배치 파일
├── start_oz_generator.bat   # [2단계] 백엔드+프론트엔드 동시 실행 및 브라우저 자동 오픈 배치 파일
└── README.md                # 인수인계 및 작업 기록 문서
```

---

## 🛠️ 핵심 구현 사항 및 원칙

1. **OZR / ODI 바이너리 규격 100% 준수**
   - **OZR 바이너리 헤더**: `OZR\x07\x00\x00\x00\x0e\x00\x00OZ Report File` (24 bytes)
   - **ODI 바이너리 헤더**: `ODI\x05\x01\x00\x01\x10\x00\x00OZ Document File` (26 bytes)
   - **VERSION 고정**: 구버전 OZ Designer 렌더링 호환을 위해 `<VERSION VERSION="7.0" .../>` 원칙 준수

2. **자동 채번 및 중복 방지 (PLA0501_R 시리즈)**
   - 파일명 저장 위치: `C:\CPE_DEV\workspace\CPE_APP\war\reports\pl\pla\`
   - 체번 원칙: `PLA0501_R` 접두사 고정 후, 기존 디렉토리 스캔을 통한 최대 R번호 + 1 자동 증번 (`PLA0501_R26.ozr`, `PLA0501_R26.odi`)

3. **엑셀 기반 자동 레이아웃 파싱 (AI API 불필요)**
   - `openpyxl`로 셀 값, 스타일, 테두리(border), 병합(merged cells) 정보 분석
   - 테두리가 있는 연속 데이터 행을 **Body**(반복 영역)로 식별
   - Body 상단 행들을 **Header**, 하단 행들을 **Footer**로 자동 분류하여 OZR Band 구조로 생성

---

## 🚀 다른 PC에서 이어서 실행하는 순서

### 사전 준비
- **Python 3.8 이상** 및 **Node.js 18 이상**이 설치된 PC 환경

### 1단계: 의존성 패키지 설치
`install_deps.bat` 파일 더블클릭
- 백엔드(`fastapi`, `uvicorn`, `openpyxl`, `sse-starlette`) 및 프론트엔드(`next`, `react`) 패키지를 자동으로 설치합니다.

### 2단계: 애플리케이션 실행
`start_oz_generator.bat` 파일 더블클릭
- FastAPI 백엔드(8088포트)와 Next.js 프론트엔드(3088포트)가 각각 독립된 터미널 창으로 켜집니다.
- 5초 후 자동으로 웹 브라우저(`http://localhost:3088`)가 열립니다.

---

## 🧪 테스트 및 사용 방법

1. 브라우저에서 `http://localhost:3000` 접속
2. 고객 요청 엑셀 파일 (`C:\CPE_DEV\workspace\CPE_APP\war\reports\pl\pla\26C17,18 Transmittal2.xlsx` 등) 업로드
3. 미리보기에서 헤더, 컬럼, 풋터 추출 결과 확인
4. **생성하기** 버튼을 클릭하여 `PLA0501_R26.ozr` 및 `PLA0501_R26.odi` 생성을 확인
