# fix_r26_binary.py
# Run this script: python fix_r26_binary.py
# This fixes PLA0501_R26.ozr and PLA0501_R26.odi by copying the exact binary
# headers from PLA0501_R24 and substituting references in the XML body.

import os

BASE = 'd:/antigra/oz'

def fix_file(ext):
    src = os.path.join(BASE, f'PLA0501_R24.{ext}')
    dst = os.path.join(BASE, f'PLA0501_R26.{ext}')
    
    with open(src, 'rb') as f:
        data = f.read()
    
    # Find where XML starts
    xml_start = data.find(b'<?xml')
    if xml_start == -1:
        print(f"ERROR: Could not find <?xml in {src}")
        return
    
    binary_header = data[:xml_start]
    xml_body = data[xml_start:].decode('utf-8')
    
    # Replace all occurrences of PLA0501_R24 with PLA0501_R26
    xml_body_new = xml_body.replace('PLA0501_R24', 'PLA0501_R26')
    count = xml_body.count('PLA0501_R24')
    
    new_data = binary_header + xml_body_new.encode('utf-8')
    
    with open(dst, 'wb') as f:
        f.write(new_data)
    
    print(f"[OK] Fixed {dst}")
    print(f"     Header bytes: {len(binary_header)} (binary, exact copy from R24)")
    print(f"     Substitutions: {count} occurrences of PLA0501_R24 -> PLA0501_R26")
    print(f"     Header hex: {binary_header.hex()}")

print("=== Fixing PLA0501_R26 files ===")
print()
fix_file('ozr')
print()
fix_file('odi')
print()
print("Done! Try opening PLA0501_R26.ozr in OZ Designer now.")
