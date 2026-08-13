"""
ODI (OZ Document Info) 파일 생성 모듈

ODI 파일은 데이터 소스 정의 파일로, OZR이 참조하는 DB 쿼리와 파라미터를 정의합니다.
기존 ODI를 템플릿으로 복사하거나, 사용자 설정 기반으로 더미 ODI를 생성합니다.
"""

import os
import re

# ODI 바이너리 헤더 (OZ Document File 포맷 마커, 26 bytes)
ODI_HEADER = b'ODI\x05\x01\x00\x01\x10\x00\x00OZ Document File'


def create_dummy_odi_xml(odi_name: str, dataset_names: list, param_fields: list = None) -> str:
    """
    더미 ODI XML을 생성합니다.
    
    Args:
        odi_name: ODI 식별자 이름 (예: "PLA0501_R26")
        dataset_names: 데이터셋 이름 목록 (예: ["DATA_LIST"])
        param_fields: 파라미터 필드 목록 (예: [{"name": "rObjectId", "value": "dummy"}])
    """
    if param_fields is None:
        param_fields = [{"name": "rObjectId", "value": "090f424080012d67"}]
    
    # 파라미터 필드 XML
    param_xml = ""
    for pf in param_fields:
        param_xml += (
            f'\t\t\t\t<PARAMFIELD NAME="{pf["name"]}" INCLUDE="" TYPE="12" '
            f'EDITFIELDTYPE="false" DESCRIPTION="" VALUE="{pf["value"]}" '
            f'SESSION_KEY="" ENCRYPTION="False"/>\r\n'
        )
    
    # 데이터셋 쿼리 XML
    query_xml = ""
    query_info_xml = ""
    for ds_name in dataset_names:
        # 기본 더미 쿼리 생성
        query_xml += (
            f'\t\t\t<OZQUERY NAME="{ds_name}" INCLUDE="" MASTERSET="" DBINFOID="PL_AP" '
            f'SCRIPT="false" MAXROW="0" HIDDEN="false" LOADSFIELDINFODYNAMICALLY="false" '
            f'SDMTYPE="0" SIGN="false" HIDEDESIGNTIME="false" ISCRIPT="false" '
            f'INSERT_ROW_QUERY="" DSCRIPT="false" DELETE_ROW_QUERY="" USCRIPT="false" '
            f'UPDATE_ROW_QUERY="" CONCURRENTFETCHSIZE="0" CONCURRENTFIRSTROW="0" '
            f'FLUSHONSTART="false" FLUSHONEND="false" DESCRIPTION="" PREPARED="false" '
            f'PREPAREDACTION="false" DESIGNMODE="" JDBCFETCHROW="0" USEANSIQUERY="true">'
            f"SELECT 'DUMMY' AS COL1 FROM DUAL"
            f'<DATAFIELD NAME="COL1" INCLUDE="" TYPE="12" EDITFIELDTYPE="false" '
            f'DESCRIPTION="" UPDATE_FIELD_QUERY="" DECRYPTION=""/>\r\n'
            f'\t\t\t</OZQUERY>\r\n'
        )
        
        query_info_xml += (
            f'\t\t\t<OZQUERYINFO STORENAME="PL_AP" SETNAME="{ds_name}">\r\n'
            f'\t\t\t\t<OZQUERYELEMENTINFO CLASSID="1006" MODE="FALSE" '
            f'WHERESTRING="" HAVINGSTRING="" DELETEDTABLES=""/>\r\n'
            f'\t\t\t</OZQUERYINFO>\r\n'
        )
    
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\r\n'
        '<OZDATAINFO>\r\n'
        '\t<OZDATAMODULE NAME="[OZ DATA Tree]" INCLUDE="" VERSION="1.0" '
        'PARAMETERFLAG="#" IGNORENULLDATA="true" SCRIPTBCE="false" '
        'CONCURRENTFETCHSIZE="0" CONNECTIONPOSITION="Default" '
        'DISPLAYZERO="Default" IGNORESCRIPTERROR="false">\r\n'
        '\t\t<OZPARAMETERSTORE NAME="paramstore">\r\n'
        '\t\t\t<OZPARAMETERSET NAME="OZParam" INCLUDE="" MASTERSET="" '
        'HIDDEN="false" LOADSFIELDINFODYNAMICALLY="false" SDMTYPE="0" '
        'SIGN="false" HIDEDESIGNTIME="false">\r\n'
        f'{param_xml}'
        '\t\t\t</OZPARAMETERSET>\r\n'
        '\t\t</OZPARAMETERSTORE>\r\n'
        '\t\t<OZFILESTORE NAME="FILESTORE" INCLUDE=""/>\r\n'
        '\t\t<OZHTTPSTORE NAME="HTTPSTORE" INCLUDE=""/>\r\n'
        '\t\t<OZDBSTORE NAME="PL_AP" INCLUDE="" VENDOR="oracle" '
        'serverAddress="" portNo="" sid="" USERNAME="" ENCYPW="" PASSWORD="" '
        'USEALIAS="true" POOLALIAS="dooit_oz" ALIASFILENAME="./db.properties" '
        'ENCODECHARSET="KSC5601" DECODECHARSET="KSC5601" AUTOCOMMIT="true" '
        'DAC_DELEGATE="" DELEGATE_INIT_PARAM="" DAC_DELEGATE_LIB="" USEPARAM="false">\r\n'
        f'{query_xml}'
        '\t\t</OZDBSTORE>\r\n'
        '\t\t<OZINCLUDESTORE NAME="includestore">\r\n'
        '\t\t\t<OZINCLUDESET NAME="includeSet" INCLUDE=""/>\r\n'
        '\t\t</OZINCLUDESTORE>\r\n'
        '\t\t<OZQUERYDESIGNERINFO>\r\n'
        f'{query_info_xml}'
        '\t\t</OZQUERYDESIGNERINFO>\r\n'
        '\t</OZDATAMODULE>\r\n'
        '</OZDATAINFO>'
    )
    
    return xml


def copy_existing_odi(source_odi_path: str, new_odi_name: str) -> bytes:
    """
    기존 ODI 파일을 복사하여 새 ODI를 생성합니다.
    바이너리 헤더는 유지하고 내부 참조만 변경합니다.
    """
    with open(source_odi_path, 'rb') as f:
        data = f.read()
    
    return data


def build_odi_file(xml_content: str) -> bytes:
    """ODI 바이너리 헤더 + XML을 결합하여 바이너리 데이터를 반환합니다."""
    return ODI_HEADER + xml_content.encode('utf-8')


def generate_odi(odi_name: str, dataset_names: list, 
                 source_odi_path: str = None, param_fields: list = None) -> bytes:
    """
    ODI 파일 바이너리를 생성합니다.
    
    source_odi_path가 주어지면 기존 파일을 복사하고,
    없으면 새로 더미 ODI를 생성합니다.
    """
    if source_odi_path and os.path.exists(source_odi_path):
        return copy_existing_odi(source_odi_path, odi_name)
    
    xml = create_dummy_odi_xml(odi_name, dataset_names, param_fields)
    return build_odi_file(xml)
