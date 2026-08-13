# Read PLA0501_R24 files and output PLA0501_R26 files directly in d:/antigra/oz

with open("d:/antigra/oz/PLA0501_R24.ozr", "r", encoding="utf-8") as f:
    ozr_text = f.read()

ozr_text_26 = ozr_text.replace("PLA0501_R24", "PLA0501_R26")

with open("d:/antigra/oz/PLA0501_R26.ozr", "w", encoding="utf-8") as f:
    f.write(ozr_text_26)


with open("d:/antigra/oz/PLA0501_R24.odi", "r", encoding="utf-8") as f:
    odi_text = f.read()

odi_text_26 = odi_text.replace("PLA0501_R24", "PLA0501_R26")
odi_text_26 = odi_text_26.replace("where row_idx < 11", "where row_idx < 5")
odi_text_26 = odi_text_26.replace("where row_idx > 10", "where row_idx > 4")

with open("d:/antigra/oz/PLA0501_R26.odi", "w", encoding="utf-8") as f:
    f.write(odi_text_26)

print("Directly wrote PLA0501_R26.ozr and PLA0501_R26.odi")
