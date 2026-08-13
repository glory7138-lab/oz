"""기존 R25 OZR 파일의 전체 XML 구조를 상세 분석"""
import re

ozr_path = r"C:\CPE_DEV\workspace\CPE_APP\war\reports\pl\pla\PLA0501_R25.ozr"
with open(ozr_path, 'rb') as f:
    data = f.read()
xml = data[24:].decode('utf-8', errors='replace')

# REPORTINFO 태그
m = re.search(r'<REPORTINFO\s([^>]+)>', xml)
if m:
    print("=== REPORTINFO attrs ===")
    for a in re.findall(r'(\w+)="([^"]*)"', m.group(1)):
        print(f"  {a[0]}={a[1]}")

# All OZBAND tags
print("\n=== OZBAND tags ===")
for m in re.finditer(r'<OZBAND\s([^>]*?)/?>', xml):
    print(f"  <OZBAND {m.group(1)[:200]}>")

# OZDATABAND
print("\n=== OZDATABAND tags ===")
for m in re.finditer(r'<OZDATABAND\s([^>]*?)/?>', xml):
    print(f"  <OZDATABAND {m.group(1)[:200]}>")

# OZTABLE
print("\n=== OZTABLE tags ===")
for m in re.finditer(r'<OZTABLE\s([^>]*?)/?>', xml):
    print(f"  <OZTABLE {m.group(1)[:300]}>")

# OZBACKBAND / OZFOREBAND
print("\n=== OZBACKBAND ===")
for m in re.finditer(r'<OZBACKBAND\s([^>]*?)/?>', xml):
    print(f"  <OZBACKBAND {m.group(1)}>")

print("\n=== OZFOREBAND ===")
for m in re.finditer(r'<OZFOREBAND\s([^>]*?)/?>', xml):
    print(f"  <OZFOREBAND {m.group(1)}>")

# OZPARAMETERTOOLBARS
print("\n=== OZPARAMETERTOOLBARS ===")
for m in re.finditer(r'<OZPARAMETER\w+\s([^>]*?)/?>', xml):
    print(f"  {m.group(0)[:100]}")

# OZODILIST / OZODIITEM
print("\n=== OZODIITEM ===")
for m in re.finditer(r'<OZODIITEM\s([^>]*?)>', xml):
    print(f"  <OZODIITEM {m.group(1)}>")

# OZFORMSETs
print("\n=== OZFORMSET ===")
for m in re.finditer(r'<OZFORMSET\s([^>]*?)/?>', xml):
    print(f"  <OZFORMSET {m.group(1)}>")

# First ONESHAPE (TitleBand header label)
print("\n=== First 3 ONESHAPE in TitleBand ===")
shapes = list(re.finditer(r'<ONESHAPE\s([^>]*?)>', xml))
for i, m in enumerate(shapes[:3]):
    print(f"  [{i}] <ONESHAPE {m.group(1)[:250]}>")

# OZTABLESTATIC
print("\n=== OZTABLESTATIC ===")
for m in re.finditer(r'<OZTABLESTATIC\s([^>]*?)/?>', xml):
    print(f"  <OZTABLESTATIC {m.group(1)[:300]}>")

# Check line endings
cr_count = xml.count('\r\r\n')
crlf_count = xml.count('\r\n')
print(f"\n=== Line endings ===")
print(f"  \\r\\r\\n count: {cr_count}")
print(f"  \\r\\n count: {crlf_count}")
