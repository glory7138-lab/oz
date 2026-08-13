"""
파일 체번/저장 관리 모듈

체번 원칙: PLA0501_R{번호} 고정, 번호만 유니크하게 자동 증가
대상 디렉토리: C:\CPE_DEV\workspace\CPE_APP\war\reports\pl\pla
"""

import os
import re

# 대상 디렉토리
REPORT_DIR = r"C:\CPE_DEV\workspace\CPE_APP\war\reports\pl\pla"

# 고정 그룹 접두사
GROUP_PREFIX = "PLA0501"

# 파일명 패턴: PLA0501_R{번호}.ozr 또는 .odi
FILE_PATTERN = re.compile(r'^PLA0501_R(\d{2,3})\.(ozr|odi)$', re.IGNORECASE)


def get_existing_files():
    """PLA0501 시리즈의 기존 파일 목록을 반환합니다."""
    if not os.path.exists(REPORT_DIR):
        return []
    
    files = []
    for fname in os.listdir(REPORT_DIR):
        match = FILE_PATTERN.match(fname)
        if match:
            r_num = int(match.group(1))
            ext = match.group(2).lower()
            files.append({
                "filename": fname,
                "r_number": r_num,
                "extension": ext,
                "full_path": os.path.join(REPORT_DIR, fname),
                "size": os.path.getsize(os.path.join(REPORT_DIR, fname))
            })
    
    return sorted(files, key=lambda x: (x["r_number"], x["extension"]))


def get_next_r_number() -> int:
    """PLA0501 시리즈의 다음 R번호를 계산합니다."""
    files = get_existing_files()
    if not files:
        return 1
    
    max_r = max(f["r_number"] for f in files)
    return max_r + 1


def generate_filename(r_number: int, ext: str) -> str:
    """파일명을 생성합니다. 예: PLA0501_R26.ozr"""
    return f"{GROUP_PREFIX}_R{r_number:02d}.{ext}"


def get_odi_ref_name(r_number: int) -> str:
    """ODI 참조 이름을 반환합니다. 예: PLA0501_R26"""
    return f"{GROUP_PREFIX}_R{r_number:02d}"


def save_file(data: bytes, r_number: int, ext: str) -> str:
    """
    파일을 대상 디렉토리에 저장하고 전체 경로를 반환합니다.
    
    Args:
        data: 파일 바이너리 데이터
        r_number: R번호
        ext: 확장자 (ozr 또는 odi)
    
    Returns:
        저장된 파일의 전체 경로
    """
    # 디렉토리 존재 확인
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR, exist_ok=True)
    
    filename = generate_filename(r_number, ext)
    filepath = os.path.join(REPORT_DIR, filename)
    
    # 중복 체크
    if os.path.exists(filepath):
        raise FileExistsError(f"파일이 이미 존재합니다: {filepath}")
    
    with open(filepath, "wb") as f:
        f.write(data)
    
    return filepath


def get_reference_odi_path() -> str:
    """
    참조용 ODI 파일 경로를 반환합니다.
    기존 PLA0501 시리즈 중 가장 작은 번호의 ODI를 반환.
    """
    files = get_existing_files()
    odi_files = [f for f in files if f["extension"] == "odi"]
    
    if odi_files:
        return odi_files[0]["full_path"]
    
    # PLA0501 시리즈에 없으면 다른 그룹에서 찾기
    all_pattern = re.compile(r'^PLA\d{4}_R\d{2,3}\.odi$', re.IGNORECASE)
    if os.path.exists(REPORT_DIR):
        for fname in sorted(os.listdir(REPORT_DIR)):
            if all_pattern.match(fname):
                return os.path.join(REPORT_DIR, fname)
    
    return None


def get_file_list_summary() -> dict:
    """파일 목록 요약 정보를 반환합니다."""
    files = get_existing_files()
    ozr_files = [f for f in files if f["extension"] == "ozr"]
    odi_files = [f for f in files if f["extension"] == "odi"]
    next_r = get_next_r_number()
    
    return {
        "total_ozr": len(ozr_files),
        "total_odi": len(odi_files),
        "max_r_number": max((f["r_number"] for f in files), default=0),
        "next_r_number": next_r,
        "next_ozr_filename": generate_filename(next_r, "ozr"),
        "next_odi_filename": generate_filename(next_r, "odi"),
        "report_dir": REPORT_DIR,
        "files": [
            {
                "filename": f["filename"],
                "r_number": f["r_number"],
                "extension": f["extension"],
                "size_kb": round(f["size"] / 1024, 1)
            }
            for f in files[-10:]  # 최근 10개만
        ]
    }
