# build_r26_final.py
# PLA0501_R24의 바이너리 헤더를 복사하고 새 XML을 붙여 PLA0501_R26.ozr / .odi 를 생성합니다.

import os

BASE = os.path.dirname(os.path.abspath(__file__))

def build_file(src_bin_path, new_xml_path, dst_path):
    """
    src_bin_path : 바이너리 헤더를 가져올 원본 파일 (R24)
    new_xml_path : 새 XML 내용 파일
    dst_path     : 최종 출력 파일
    """
    # R24에서 바이너리 헤더 추출
    with open(src_bin_path, 'rb') as f:
        data = f.read()
    xml_start = data.find(b'<?xml')
    binary_header = data[:xml_start]

    # 새 XML 내용 읽기
    with open(new_xml_path, 'r', encoding='utf-8') as f:
        xml_text = f.read()

    # 결합하여 저장
    new_data = binary_header + xml_text.encode('utf-8')
    with open(dst_path, 'wb') as f:
        f.write(new_data)

    print(f"[OK] {dst_path}")
    print(f"     Binary header : {len(binary_header)} bytes  hex={binary_header.hex()}")
    print(f"     XML body      : {len(xml_text.encode('utf-8'))} bytes")
    print(f"     Total         : {len(new_data)} bytes")

print("=== Building PLA0501_R26 files ===\n")

# OZR 생성
build_file(
    src_bin_path = os.path.join(BASE, 'PLA0501_R24.ozr'),
    new_xml_path = os.path.join(BASE, 'PLA0501_R26_new.xml'),
    dst_path     = os.path.join(BASE, 'PLA0501_R26.ozr')
)

print()

# ODI 생성
build_file(
    src_bin_path = os.path.join(BASE, 'PLA0501_R24.odi'),
    new_xml_path = os.path.join(BASE, 'PLA0501_R26_odi_new.xml'),
    dst_path     = os.path.join(BASE, 'PLA0501_R26.odi')
)

print("\n=== Done! PLA0501_R26.ozr / PLA0501_R26.odi 생성 완료 ===")
print("OZ Designer 에서 PLA0501_R26.ozr 를 열어서 확인해 주세요.")
