# create_r26_final.py
# 이 스크립트를 더블클릭하거나 cmd에서 실행하세요:
#   python d:\antigra\oz\create_r26_final.py

import os

BASE = os.path.dirname(os.path.abspath(__file__))

# OZR 바이너리 헤더 (OZ Report File 포맷 마커, 24 bytes)
# OZR + version bytes + "OZ Report File"
OZR_HEADER = b'OZR\x07\x00\x00\x00\x0e\x00\x00OZ Report File'

# ODI 바이너리 헤더 (OZ Document File 포맷 마커, 26 bytes)
# ODI + version bytes + "OZ Document File"
ODI_HEADER = b'ODI\x05\x01\x00\x01\x10\x00\x00OZ Document File'

def create_oz_file(header_bytes, xml_path, out_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_text = f.read()
    # XML 선언 앞에 바이너리 헤더 삽입
    result = header_bytes + xml_text.encode('utf-8')
    with open(out_path, 'wb') as f:
        f.write(result)
    print(f"[OK] {out_path}")
    print(f"     헤더: {len(header_bytes)} bytes  |  XML: {len(xml_text.encode('utf-8'))} bytes  |  합계: {len(result)} bytes")
    # 처음 5글자 확인
    with open(out_path, 'rb') as f:
        check = f.read(30)
    print(f"     파일 시작 hex: {check.hex()}")

print("=" * 50)
print("  PLA0501_R26 파일 생성 시작")
print("=" * 50)
print()

# OZR 파일 생성
create_oz_file(
    header_bytes = OZR_HEADER,
    xml_path     = os.path.join(BASE, 'PLA0501_R26_new.xml'),
    out_path     = os.path.join(BASE, 'PLA0501_R26.ozr')
)
print()

# ODI 파일 생성
create_oz_file(
    header_bytes = ODI_HEADER,
    xml_path     = os.path.join(BASE, 'PLA0501_R26_odi_new.xml'),
    out_path     = os.path.join(BASE, 'PLA0501_R26.odi')
)

print()
print("=" * 50)
print("  완료! PLA0501_R26.ozr / .odi 생성 완료")
print("  OZ Designer에서 PLA0501_R26.ozr를 열어주세요.")
print("=" * 50)
input("\n[Enter] 키를 누르면 창이 닫힙니다...")
