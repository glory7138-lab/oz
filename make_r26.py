import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 1. R24 원본 읽기
with open(os.path.join(BASE, 'PLA0501_R24.ozr'), 'rb') as f:
    r24_ozr_raw = f.read()

with open(os.path.join(BASE, 'PLA0501_R24.odi'), 'rb') as f:
    r24_odi_raw = f.read()

# 2. OZR 텍스트 변환 및 PLA0501_R24 -> PLA0501_R26 치환
xml_start_ozr = r24_ozr_raw.find(b'<?xml')
hdr_ozr = r24_ozr_raw[:xml_start_ozr]
body_ozr = r24_ozr_raw[xml_start_ozr:].decode('utf-8')
body_ozr_r26 = body_ozr.replace('PLA0501_R24', 'PLA0501_R26')

# 3. ODI 텍스트 변환 및 PLA0501_R24 -> PLA0501_R26 치환
xml_start_odi = r24_odi_raw.find(b'<?xml')
hdr_odi = r24_odi_raw[:xml_start_odi]
body_odi = r24_odi_raw[xml_start_odi:].decode('utf-8')
body_odi_r26 = body_odi.replace('PLA0501_R24', 'PLA0501_R26')

# 4. 파일 저장
with open(os.path.join(BASE, 'PLA0501_R26.ozr'), 'wb') as f:
    f.write(hdr_ozr + body_ozr_r26.encode('utf-8'))

with open(os.path.join(BASE, 'PLA0501_R26.odi'), 'wb') as f:
    f.write(hdr_odi + body_odi_r26.encode('utf-8'))

print("Clone successfully created!")
