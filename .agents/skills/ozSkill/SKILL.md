---
name: ozSkill
description: Rules for OZR report font alignment, font size, cell margins, and single-line text overflow prevention extracted from R25 OZR XML analysis.
---

# ozSkill: OZR Text Formatting & Single-Line Layout Rules

This skill documents the XML formatting rules extracted from `PLA0501_R25.ozr` to achieve 100% visual consistency and structural alignment in generated OZ Reports.

---

## 1. Global Label Rules (`<BASICLABEL>`)

`<BASICLABEL>` defines default text formatting for all labels and table cells in the report:

```xml
<BASICLABEL 
  WIDTH="100" 
  HEIGHT="20" 
  BGCOLOR="-1" 
  TRANSPARENT="false" 
  BackgroundAlpha="255" 
  CLIP="false" 
  DRAWLEFT="0.125" DRAWTOP="0.125" DRAWRIGHT="0.125" DRAWBOTTOM="0.125" 
  FRAMECOLORLEFT="-16777216" FRAMECOLORTOP="-16777216" FRAMECOLORRIGHT="-16777216" FRAMECOLORBOTTOM="-16777216" 
  FrameDrawingMode="2" 
  FGCOLOR="-16777216" 
  FONTNAME="맑은 고딕" 
  FONTSIZE="10" 
  FONTSTYLE="0" 
  STRETCHTYPE="1" 
  HALIGN="0" 
  VALIGN="0" 
  EFFECT="Basic" 
  SPACING="0" 
  FONTSTRETCH="100" 
  WRAPSPACE="0" 
  LEFTMARGIN="2" 
  TOPMARGIN="0" 
  RIGHTMARGIN="2" 
  BOTTOMMARGIN="0" 
  AUTOSIZE="false" 
  AUTOFONTSIZE="false" 
  WORDWRAP="false" 
  WORDWRAPTYPE="1" 
  CRLFTOLF="false" 
  TABCOUNT="4" 
  USEGRADIENT="False" 
  GRADIENTCOLOR="-1" 
  GRADIENTTYPE="6"/>
```

---

## 2. Text Alignment Rules (`HALIGN` & `VALIGN`)

| Tag | Alignment Attribute | Value | Description |
| :--- | :--- | :--- | :--- |
| `<BASICLABEL>` | `HALIGN="0"` | `0` (Left) | Default horizontal text alignment |
| `<BASICLABEL>` | `VALIGN="0"` | `0` (Top) | Default vertical text alignment |
| `<OZTABLELABEL>` | `HALIGN="1"` / `VALIGN="1"` | `1` (Center) | Header & approval box labels centered |
| `<OZTTLABEL>` | `HALIGN="1"` | `1` (Center) | Data band table headers centered |
| `<OZGROUPLABEL>` | `HALIGN` (dynamic) | `0` / `1` / `2` | Left (`0`) for text, Center (`1`) for codes/dates/status, Right (`2`) for amounts |

- **Excel Mapping**:
  - `horizontal`: `left` / `general` -> `HALIGN="0"`, `center` -> `HALIGN="1"`, `right` -> `HALIGN="2"`
  - `vertical`: `top` -> `VALIGN="0"`, `center` / `middle` -> `VALIGN="1"`, `bottom` -> `VALIGN="2"`

---

## 3. Font Size & Style Rules (`FONTSIZE` & `FONTSTYLE`)

1. **Default Font**: `FONTNAME="맑은 고딕"` (or `굴림`), `FONTSIZE="10"`.
2. **Font Style**:
   - `FONTSTYLE="0"`: Regular (Normal weight)
   - `FONTSTYLE="1"`: Bold
3. **Table Title & Data Font Sizes**:
   - Table title headers (`OZTTLABEL`): Match Excel cell font size or default `10` with `FONTSTYLE="1"`.
   - Data values (`OZGROUPLABEL`): Match Excel cell font size or default `10`.

---

## 4. Single-Line Text Overflow Prevention Rules (한 줄 넘침 방지)

To prevent text from wrapping into multiple lines or overflowing outside table column cells:

1. **`WORDWRAP="false"`**:
   - Explicitly disable multi-line word wrapping on table labels and cells so text stays strictly on one line.
2. **`AUTOFONTSIZE="smallerOnly"`**:
   - Set on `<OZGROUPLABEL>`. If data text is longer than column width, OZ Report automatically reduces font size so text stays within the cell without wrapping or getting truncated.
3. **`AUTOSIZE="false"`**:
   - Prevents table cell bounding boxes from unpredictably altering row heights or column widths.
4. **`LEFTMARGIN="2" RIGHTMARGIN="2"`**:
   - Provides 2pt horizontal padding inside cell borders so text does not clip or touch cell frame lines.
5. **Narrow Column Vertical Title Headers (`STRETCHTYPE="5"`)**:
   - For narrow columns (e.g. `A1`~`A13` revision status columns with width ~15-18pt), set `STRETCHTYPE="5"`, `HSTRETCH="false"`, `VSTRETCH="false"` so text headers handle space without text overflow.

## 5. Table Header & Data Row Zero-Gap Alignment Rule (헤더-데이터 100% 밀착)

In OZ Report `<OZTABLE>` structures, dataset data rows (`<OZGROUPLABEL>`) **must ALWAYS be attached directly below** the table header title cells (`<OZTTLABEL>`), with ZERO vertical gap and NO extra intermediate blank rows:

1. **Direct Attachment**: `table_data_cells` `top` = `max_header_bottom` (where `max_header_bottom` = max(`top` + `height`) of all `<OZTTLABEL>` cells).
2. **Intermediate Row Elimination**: Any blank/mock rows present between header titles and dataset rows in source Excel templates are automatically ignored and excluded from the Table Header calculations.
3. **Seamless Repetition**: When OZ Report engine iterates dataset records at runtime, rows repeat directly under the header without creating extraneous spacing.

---

## 6. Vertically Merged Cells & Vertical Text (세로 병합 셀의 세로 글쓰기)

When cells are vertically merged (spanning multiple rows but constrained to a single column), the text must be formatted to read vertically:

1. **Character Stack**: Ensure vertical text flow by inserting XML newline sequences (`&#xD;&#xA;`) between every character in the string (if not already separated by spaces/newlines).
2. **Automatic Wrapping**: Do NOT rely purely on `WORDWRAP="true"` for vertical text in vertically merged columns; explicit insertion of newlines guarantees proper rendering in OZ Report.
