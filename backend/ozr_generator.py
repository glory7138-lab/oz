"""
OZR (OZ Report) 파일 생성 모듈 (정확한 좌표 및 데이터 바인딩 적용)
"""

import time
import html
import re

OZR_HEADER = b'OZR\x07\x00\x00\x00\x0e\x00\x00OZ Report File'

PAPER_WIDTH = 842
PAPER_HEIGHT = 595
LEFT_MARGIN = 19.991
TOP_MARGIN = 15.011
RIGHT_MARGIN = 15.991
BOTTOM_MARGIN = 0
CONTENT_WIDTH = PAPER_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
CONTENT_HEIGHT = PAPER_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

def escape_xml(text: str) -> str:
    return html.escape(str(text), quote=True)

def _build_version():
    timestamp = int(time.time() * 1000)
    return f'<VERSION VERSION="7.0" DATE="{timestamp}"/>'

def _build_basic_label():
    return (
        '<BASICLABEL WIDTH="100" HEIGHT="20" BGCOLOR="-1" TRANSPARENT="false" '
        'BackgroundAlpha="255" CLIP="false" DRAWLEFT="0.125" DRAWTOP="0.125" '
        'DRAWRIGHT="0.125" DRAWBOTTOM="0.125" DASHLEFT="" DASHTOP="" '
        'DASHRIGHT="" DASHBOTTOM="" DASHOFFSETLEFT="" DASHOFFSETTOP="" '
        'DASHOFFSETRIGHT="" DASHOFFSETBOTTOM="" FRAMECOLORLEFT="-16777216" '
        'FRAMECOLORTOP="-16777216" FRAMECOLORRIGHT="-16777216" '
        'FRAMECOLORBOTTOM="-16777216" FrameDrawingMode="2" RADIUSTOPLEFT="0" '
        'RADIUSTOPRIGHT="0" RADIUSBOTTOMRIGHT="0" RADIUSBOTTOMLEFT="0" '
        'FGCOLOR="-16777216" FONTNAME="맑은 고딕" FONTSIZE="10" FONTSTYLE="0" '
        'STRETCHTYPE="1" HALIGN="0" VALIGN="0" TEXTROTATION="0" '
        'EFFECT="Basic" SPACING="0" FONTSTRETCH="100" WRAPSPACE="0" '
        'LEFTMARGIN="2" TOPMARGIN="0" RIGHTMARGIN="2" BOTTOMMARGIN="0" '
        'AUTOSIZE="false" AUTOFONTSIZE="false" WORDWRAP="false" '
        'WORDWRAPTYPE="1" CRLFTOLF="false" TABCOUNT="4" '
        'USEGRADIENT="False" GRADIENTCOLOR="-1" GRADIENTTYPE="6"/>'
    )

def _build_default_label():
    return '<DEFAULTLABEL TABCOUNT="4"/>'

def _build_static_table_labels(labels: list, prefix: str) -> str:
    """OZTABLELABEL 들을 생성합니다."""
    xml = []
    for idx, lbl in enumerate(labels):
        text = escape_xml(lbl.get("text", ""))
        left = round(lbl.get("left", 0), 3)
        top = round(lbl.get("top", 0), 3)
        width = round(lbl.get("width", 100), 3)
        height = round(lbl.get("height", 20), 3)
        h_align = lbl.get("h_align", "0")
        v_align = lbl.get("v_align", "1")
        font_size = lbl.get("font_size", 10)
        font_style = "1" if lbl.get("bold") else "0"
        
        border_attrs = 'DRAWLEFT="1" DRAWTOP="1" DRAWRIGHT="1" DRAWBOTTOM="1" ' if lbl.get("has_border") else ""
        bg_color_attr = f'BGCOLOR="14803425" ' if lbl.get("bg_color") != "none" and lbl.get("bg_color") else ""
        
        xml.append(
            f'<OZTABLELABEL NAME="{prefix}{idx+1}" LEFT="{left}" TOP="{top}" '
            f'WIDTH="{width}" HEIGHT="{height}" '
            f'DASHOFFSETLEFT="0" DASHOFFSETTOP="0" DASHOFFSETRIGHT="0" DASHOFFSETBOTTOM="0" '
            f'{border_attrs}{bg_color_attr}'
            f'FONTSIZE="{font_size}" FONTSTYLE="{font_style}" HALIGN="{h_align}" VALIGN="{v_align}">'
            f'{text}</OZTABLELABEL>'
        )
    return "\r\n".join(xml)

def _build_page_header_band(header_config: dict, content_width: float) -> tuple:
    height = round(header_config.get("height", 50), 3)
    labels = header_config.get("labels", [])
    
    labels_xml = _build_static_table_labels(labels, "FixedTableLabel")
    count = len(labels)
    
    band = (
        f'<OZBAND NAME="PageHeaderBand1" WIDTH="{content_width}" '
        f'HEIGHT="{height}" BANDTYPE="1" COUNT="{count}">\r\n'
        f'<OZTABLESTATIC NAME="FixedTable1" LEFT="0" TOP="0" '
        f'WIDTH="{content_width}" HEIGHT="{height}">\r\n'
        f'{labels_xml}\r\n'
        f'</OZTABLESTATIC>\r\n'
        f'</OZBAND>'
    )
    return band, height

def _build_data_band_with_table(body_config: dict, content_width: float, odi_name: str, band_top: float) -> tuple:
    height = round(body_config.get("height", 40), 3)
    title_labels = body_config.get("title_labels", [])
    data_labels = body_config.get("data_labels", [])
    
    # 엑셀 전체 폭이 OZ용지 폭과 다를 수 있으므로 폭을 content_width에 맞추거나 그대로 둡니다.
    # 여기서는 추출된 정확한 좌표 그대로 사용합니다.
    table_width = content_width
    
    titles_xml = []
    for idx, lbl in enumerate(title_labels):
        raw_text = lbl.get("text", "")
        text = escape_xml(raw_text)
        if lbl.get("vertically_merged") and raw_text and " " not in raw_text and "\n" not in raw_text:
            text = "&#xD;&#xA;".join(list(text))
        left = round(lbl.get("left", 0), 3)
        top = round(lbl.get("top", 0), 3)
        width = round(lbl.get("width", 100), 3)
        h = round(lbl.get("height", 20), 3)
        h_align = lbl.get("h_align", "1")
        v_align = lbl.get("v_align", "1")
        font_size = lbl.get("font_size", 10)
        font_style = "1" if lbl.get("bold") else "0"
        
        border_attrs = 'DRAWLEFT="1" DRAWTOP="1" DRAWRIGHT="1" DRAWBOTTOM="1" ' if lbl.get("has_border") else 'DRAWLEFT="0" DRAWTOP="0" DRAWRIGHT="0" DRAWBOTTOM="0" '
        bg_color_attr = f'BGCOLOR="-5186329" ' if lbl.get("bg_color") != "none" else ""
        stretch_attr = 'STRETCHTYPE="5" HSTRETCH="false" VSTRETCH="false" ' if width < 22 else ""
        
        titles_xml.append(
            f'<OZTTLABEL NAME="TableTitle{idx + 1}" LEFT="{left}" TOP="{top}" '
            f'WIDTH="{width}" HEIGHT="{h}" '
            f'{bg_color_attr}{border_attrs}{stretch_attr}'
            f'DASHOFFSETLEFT="0" DASHOFFSETTOP="0" DASHOFFSETRIGHT="0" DASHOFFSETBOTTOM="0" '
            f'FONTSIZE="{font_size}" FONTSTYLE="{font_style}" HALIGN="{h_align}" VALIGN="{v_align}" TABLEINDEX="{idx}">{text}</OZTTLABEL>'
        )
        
    values_xml = []
    field_items = []
    sell_labels = []
    datasets = set()
    
    for idx, lbl in enumerate(data_labels):
        text = lbl.get("text", "")
        left = round(lbl.get("left", 0), 3)
        top = round(lbl.get("top", 0), 3)
        width = round(lbl.get("width", 100), 3)
        h = round(lbl.get("height", 20), 3)
        h_align = lbl.get("h_align", "0")
        v_align = lbl.get("v_align", "1")
        font_size = lbl.get("font_size", 10)
        font_style = "1" if lbl.get("bold") else "0"
        
        border_attrs = 'DRAWLEFT="1" DRAWTOP="1" DRAWRIGHT="1" DRAWBOTTOM="1" ' if lbl.get("has_border") else 'DRAWLEFT="0" DRAWTOP="0" DRAWRIGHT="0" DRAWBOTTOM="0" '
        
        # <DATASET:COLNAME> 파싱
        dataset_name = "TR_VIEW"
        col_name = f"COL{idx+1}"
        m = re.search(r'<([^:]+):([^>]+)>', text)
        if m:
            dataset_name = m.group(1)
            col_name = m.group(2)
        else:
            # R25 mapping for missing tags in template
            mapping = {
                0: "DOC_NO", 1: "REV_NO", 2: "TITLE", 3: "CLIENT_DOC_NO", 4: "DOC_CLASS",
                5: "A1", 6: "A2", 7: "A3", 8: "A4", 9: "A5", 10: "A6", 11: "A7",
                12: "A8", 13: "A9", 14: "A10", 15: "A11", 16: "A12", 17: "A13"
            }
            if idx in mapping:
                col_name = mapping[idx]
        
        datasets.add(dataset_name)
        field_items.append(str(idx))
        sell_labels.append(col_name)
        
        values_xml.append(
            f'<OZGROUPLABEL NAME="TableValue{idx + 1}" LEFT="{left}" '
            f'TOP="{top}" WIDTH="{width}" HEIGHT="{h}" '
            f'ODINAME="{odi_name}" DATASETNAME="{dataset_name}" '
            f'COLNAME="{col_name}" '
            f'{border_attrs}'
            f'DASHOFFSETLEFT="0" DASHOFFSETTOP="0" DASHOFFSETRIGHT="0" DASHOFFSETBOTTOM="0" '
            f'FONTSIZE="{font_size}" FONTSTYLE="{font_style}" HALIGN="{h_align}" VALIGN="{v_align}" '
            f'AUTOSIZE="false" AUTOFONTSIZE="smallerOnly" NULLTYPE="5" '
            f'PRIORLABELNAME="Root" TABLEINDEX="{idx}">{col_name}</OZGROUPLABEL>'
        )
        
    field_items_str = "#%$oz*&amp;^".join(field_items)
    sell_labels_str = "#%$oz*&amp;^".join(sell_labels)
    default_dataset = list(datasets)[0] if datasets else "TR_VIEW"
    
    titles_xml_str = "\r\n".join(titles_xml)
    values_xml_str = "\r\n".join(values_xml)
    
    table_xml = (
        f'<OZTABLE NAME="Table1" WIDTH="{table_width}" HEIGHT="{height}" '
        f'ODINAME="{odi_name}" DATASET="{default_dataset}" '
        f'HAVETITLE="true" '
        f'TABLEFIELDITEMS="{field_items_str}" '
        f'TABLETITLEITEMS="{field_items_str}" '
        f'SELLABEL="{sell_labels_str}">\r\n'
        f'{titles_xml_str}\r\n'
        f'{values_xml_str}\r\n'
        f'</OZTABLE>'
    )
    
    band = (
        f'<OZDATABAND NAME="DataBand1" LEFT="0" TOP="{band_top}" '
        f'WIDTH="{content_width}" HEIGHT="{height}" '
        f'ODINAME="{odi_name}" MASTER="Report1" BANDTYPE="4" COUNT="1" '
        f'HEADERDUMMY="" FOOTERDUMMY="" SUBDATALIST="" UMDFIELDLIST="" '
        f'DATASOURCENAME="{default_dataset}">\r\n'
        f'{table_xml}\r\n'
        f'</OZDATABAND>'
    )
    return band, height, list(datasets)

def _build_page_footer_band(footer_config: dict, content_width: float, content_height: float) -> tuple:
    height = round(footer_config.get("height", 30), 3)
    labels = footer_config.get("labels", [])
    footer_top = content_height - height
    
    labels_xml = _build_static_table_labels(labels, "FixedTableLabel")
    count = len(labels)
    
    band = (
        f'<OZBAND NAME="PageFooterBand1" LEFT="0" TOP="{footer_top}" '
        f'WIDTH="{content_width}" HEIGHT="{height}" BANDTYPE="9" COUNT="{count}">\r\n'
        f'<OZTABLESTATIC NAME="FixedTable2" LEFT="0" TOP="0" '
        f'WIDTH="{content_width}" HEIGHT="{height}">\r\n'
        f'{labels_xml}\r\n'
        f'</OZTABLESTATIC>\r\n'
        f'</OZBAND>'
    )
    return band, height

def _build_odi_list(odi_ref_name: str, odi_filename: str, dataset_names: list) -> str:
    formsets = "\r\n".join(
        f'<OZFORMSET NAME="{ds}"/>' for ds in dataset_names
    )
    param_formset = (
        '<OZFORMSET NAME="OZParam">\r\n'
        '<PARAMFIELD FIELDNAME="rObjectId" VALUE="090186a08052e65e"/>\r\n'
        '</OZFORMSET>'
    )
    return (
        f'<OZODILIST>\r\n'
        f'<OZODIITEM NAME="{odi_ref_name}" CATEGORY="pl/pla" ODINAME="{odi_filename}">\r\n'
        f'{formsets}\r\n'
        f'{param_formset}\r\n'
        f'</OZODIITEM>\r\n'
        f'<OZFORMPARAMS/>\r\n'
        f'<OZRESOURCES/>\r\n'
        f'</OZODILIST>'
    )

def generate_ozr_xml(config: dict) -> str:
    odi_ref_name = config.get("odi_ref_name", "REPORT_ODI")
    odi_filename = config.get("odi_filename", "report.odi")
    header_config = config.get("header", {})
    body_config = config.get("body", {})
    footer_config = config.get("footer", {})
    
    content_width = round(CONTENT_WIDTH, 3)
    content_height = round(CONTENT_HEIGHT, 3)
    
    bands = []
    
    header_band_xml, header_height = _build_page_header_band(header_config, content_width)
    bands.append(header_band_xml)
    
    current_top = header_height
    
    data_band_xml, data_height, body_datasets = _build_data_band_with_table(
        body_config, content_width, odi_ref_name, current_top
    )
    bands.append(data_band_xml)
    current_top += data_height
    
    footer_band_xml, footer_height = _build_page_footer_band(footer_config, content_width, content_height)
    bands.append(footer_band_xml)
    
    bands.append(
        f'<OZBACKBAND NAME="BackgroundBand1" WIDTH="{content_width}" '
        f'HEIGHT="{content_height}" BANDTYPE="101"/>'
    )
    bands.append(
        f'<OZFOREBAND NAME="ForegroundBand1" WIDTH="{content_width}" '
        f'HEIGHT="{content_height}" BANDTYPE="103"/>'
    )
    
    bands_xml = "\r\n".join(bands)
    
    dataset_names = set(body_datasets)
    dataset_names.add("TR_LIST")
    dataset_names.add("TR_VIEW")
    
    odi_list = _build_odi_list(odi_ref_name, odi_filename, list(dataset_names))
    
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        f'<OZREPORT WIDTH="{content_width}" HEIGHT="{content_height}" '
        f'VIRTUALX="1.4" VIRTUALY="1.4" '
        f'MAPMODE="4" DisplayDPI="96" FontDPI="0" '
        f'REPORT_PREVIEW_OPTION="viewer.smartframesize=true" '
        f'REPORTTYPE="1" GRIDSIZE="0.567, 0.567" JSCRIPTRULE="1" '
        f'InputVertRule="true" InputVertAlign="true" '
        f'InputBoxMultiLineRule="true" InputTextExVertAlign="true" '
        f'SCREENTOOL="1" IGNORENULLDATA="false" '
        f'Language="ko/KR" LEFTMARGIN="{LEFT_MARGIN}" TOPMARGIN="{TOP_MARGIN}" '
        f'RIGHTMARGIN="{RIGHT_MARGIN}" BOTTOMMARGIN="{BOTTOM_MARGIN}" '
        f'BookBinding="false" Orientation="false" '
        f'PAPERWIDTH="{PAPER_WIDTH}" PAPERHEIGHT="{PAPER_HEIGHT}">\r\n'
        f'{_build_version()}\r\n'
        f'{_build_basic_label()}\r\n'
        f'{_build_default_label()}\r\n'
        f'<EVENT NAME="OnStartUp" EVENTTYPE="Any" '
        f'EVENTVALUE="SetReportOption(&quot;viewer.paper_orientation&quot;,&quot;horizontal&quot;);"/>\r\n'
        f'<REPORTINFO NAME="Report1" ReportVirtualSize="{content_width}, {content_height}" '
        f'LEFTMARGIN="{LEFT_MARGIN}" TOPMARGIN="{TOP_MARGIN}" '
        f'RIGHTMARGIN="{RIGHT_MARGIN}" BOTTOMMARGIN="{BOTTOM_MARGIN}" '
        f'BOOKBINDING="0" SUBDATALIST="DataBand1" '
        f'ORIENTATION="false" '
        f'PAPERWIDTH="{PAPER_WIDTH}" PAPERHEIGHT="{PAPER_HEIGHT}" '
        f'DRAWLEFT="0" DRAWTOP="0" DRAWRIGHT="0" DRAWBOTTOM="0" '
        f'WIDTH="{content_width}" HEIGHT="{content_height}">\r\n'
        f'{bands_xml}\r\n'
        f'</REPORTINFO>\r\n'
        f'<OZPARAMETERTOOLBARS NAME="ParameterToolbar1"/>\r\n'
        f'<OZFONTDESC>\r\n<OZFONTFAMILY/>\r\n</OZFONTDESC>\r\n'
        f'{odi_list}\r\n'
        f'<OZGRIDINFO GRIDOPERATE="False" GRIDSHOW="False" '
        f'GRIDX="0.567" GRIDY="0.567" GRIDTYPE="1"/>\r\n'
        f'<OZFORMIDINFO/>\r\n'
        f'</OZREPORT>\r\n'
    )
    
    return xml

def build_ozr_file(xml_content: str) -> bytes:
    return OZR_HEADER + xml_content.encode('utf-8')

def generate_ozr(config: dict) -> bytes:
    xml = generate_ozr_xml(config)
    return build_ozr_file(xml)
