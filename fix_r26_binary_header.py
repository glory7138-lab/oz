# This script rebuilds PLA0501_R26.ozr and PLA0501_R26.odi by copying the exact
# binary header from PLA0501_R24 files and then substituting R24->R26 in the XML body.

import os

def rebuild_binary_file(src_path, dst_path, old_name, new_name):
    """
    Reads src_path in binary mode, finds the <?xml start,
    copies the binary header verbatim, then substitutes old_name->new_name in the XML text body,
    and writes to dst_path in binary mode.
    """
    with open(src_path, 'rb') as f:
        data = f.read()

    xml_start = data.find(b'<?xml')
    if xml_start == -1:
        # No XML found, just do text replace
        xml_start = 0

    header_bytes = data[:xml_start]
    xml_bytes = data[xml_start:]

    # Decode the XML body as UTF-8 and substitute references
    xml_text = xml_bytes.decode('utf-8')
    xml_text = xml_text.replace(old_name, new_name)
    new_xml_bytes = xml_text.encode('utf-8')

    # Combine binary header + new XML body
    new_data = header_bytes + new_xml_bytes

    with open(dst_path, 'wb') as f:
        f.write(new_data)

    print(f"Written: {dst_path}")
    print(f"  Header: {len(header_bytes)} bytes (binary, verbatim from source)")
    print(f"  XML body: {len(new_xml_bytes)} bytes")
    print(f"  Total: {len(new_data)} bytes")


# Rebuild OZR
rebuild_binary_file(
    src_path='d:/antigra/oz/PLA0501_R24.ozr',
    dst_path='d:/antigra/oz/PLA0501_R26.ozr',
    old_name='PLA0501_R24',
    new_name='PLA0501_R26'
)

print()

# Rebuild ODI
rebuild_binary_file(
    src_path='d:/antigra/oz/PLA0501_R24.odi',
    dst_path='d:/antigra/oz/PLA0501_R26.odi',
    old_name='PLA0501_R24',
    new_name='PLA0501_R26'
)

print()
print("Done! Both files rebuilt with correct binary headers.")
print("Now verify the headers match between R24 and R26:")
for ext in ['ozr', 'odi']:
    src = f'd:/antigra/oz/PLA0501_R24.{ext}'
    dst = f'd:/antigra/oz/PLA0501_R26.{ext}'
    with open(src, 'rb') as f:
        src_hdr = f.read(50)
    with open(dst, 'rb') as f:
        dst_hdr = f.read(50)
    xml_pos_src = src_hdr.find(b'<?xml')
    xml_pos_dst = dst_hdr.find(b'<?xml')
    print(f"\n{ext.upper()}:")
    print(f"  R24 header ({xml_pos_src} bytes): {src_hdr[:xml_pos_src].hex()}")
    print(f"  R26 header ({xml_pos_dst} bytes): {dst_hdr[:xml_pos_dst].hex()}")
    print(f"  Headers match: {src_hdr[:xml_pos_src] == dst_hdr[:xml_pos_dst]}")
