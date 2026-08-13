"""
OZ Report 자동 생성기 - FastAPI 백엔드 서버

엔드포인트:
  POST /api/generate    - XLSX 업로드 → OZR/ODI 자동 생성
  GET  /api/progress/{id} - SSE 실시간 진행상태
  GET  /api/files       - 기존 파일 목록
  GET  /api/next-number - 다음 체번 조회
  POST /api/preview     - XLSX 분석 미리보기
"""

import asyncio
import json
import os
import shutil
import time
import uuid
from typing import Dict

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from file_manager import (
    get_next_r_number, save_file, generate_filename,
    get_odi_ref_name, get_file_list_summary, get_reference_odi_path,
    REPORT_DIR
)
from xlsx_parser import parse_xlsx, get_xlsx_summary
from ozr_generator import generate_ozr, generate_ozr_xml, build_ozr_file
from odi_generator import generate_odi, build_odi_file, create_dummy_odi_xml

app = FastAPI(title="OZ Report Generator", version="1.0.0")

# CORS 설정 (Next.js 프론트엔드 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3088", "http://127.0.0.1:3088", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 진행상태 저장소
progress_store: Dict[str, list] = {}

# 임시 파일 디렉토리
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)


def add_progress(task_id: str, step: str, message: str, percent: int, status: str = "processing"):
    """진행상태를 추가합니다."""
    if task_id not in progress_store:
        progress_store[task_id] = []
    
    entry = {
        "step": step,
        "message": message,
        "percent": percent,
        "status": status,
        "timestamp": time.time()
    }
    progress_store[task_id].append(entry)


@app.get("/")
async def root():
    return {"message": "OZ Report Generator API", "version": "1.0.0"}


@app.get("/api/files")
async def list_files():
    """기존 PLA0501 파일 목록을 반환합니다."""
    try:
        summary = get_file_list_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/next-number")
async def next_number():
    """다음 R번호를 반환합니다."""
    try:
        r_num = get_next_r_number()
        return {
            "next_r_number": r_num,
            "ozr_filename": generate_filename(r_num, "ozr"),
            "odi_filename": generate_filename(r_num, "odi"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preview")
async def preview_xlsx(file: UploadFile = File(...)):
    """XLSX 파일을 분석하여 미리보기 정보를 반환합니다."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="XLSX 파일만 업로드 가능합니다.")
    
    # 임시 저장
    temp_path = os.path.join(TEMP_DIR, f"preview_{uuid.uuid4().hex[:8]}_{file.filename}")
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        parsed = parse_xlsx(temp_path)
        summary = get_xlsx_summary(parsed)
        
        return JSONResponse(content={
            "success": True,
            "summary": summary,
            "next_r_number": get_next_r_number(),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 분석 실패: {str(e)}")
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file {temp_path}: {e}")


@app.post("/api/generate")
async def generate_report(file: UploadFile = File(...)):
    """
    XLSX 파일을 업로드하면 OZR + ODI 파일을 자동 생성합니다.
    SSE로 진행상태를 스트리밍합니다.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="XLSX 파일만 업로드 가능합니다.")
    
    task_id = uuid.uuid4().hex[:12]
    
    # 임시 저장
    temp_path = os.path.join(TEMP_DIR, f"gen_{task_id}_{file.filename}")
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 비동기로 생성 시작
    asyncio.create_task(_generate_async(task_id, temp_path))
    
    return JSONResponse(content={
        "task_id": task_id,
        "message": "생성 작업이 시작되었습니다.",
        "progress_url": f"/api/progress/{task_id}"
    })


async def _generate_async(task_id: str, xlsx_path: str):
    """비동기로 OZR/ODI 파일을 생성합니다."""
    try:
        # Step 1: XLSX 분석
        add_progress(task_id, "analyze", "📋 엑셀 파일 분석 중...", 10)
        await asyncio.sleep(0.5)
        
        parsed = parse_xlsx(xlsx_path)
        summary = get_xlsx_summary(parsed)
        
        add_progress(task_id, "analyze_done", 
                     f"✅ 분석 완료: 헤더 {summary['header_labels_count']}개, "
                     f"데이터 영역 라벨 {summary['body_data_labels_count']}개, "
                     f"풋터 {summary['footer_labels_count']}개",
                     25)
        await asyncio.sleep(0.3)
        
        # Step 2: R번호 채번
        r_number = get_next_r_number()
        odi_ref = get_odi_ref_name(r_number)
        odi_filename = generate_filename(r_number, "odi")
        ozr_filename = generate_filename(r_number, "ozr")
        
        add_progress(task_id, "numbering", 
                     f"🔢 파일 번호 채번: R{r_number:02d} ({ozr_filename})",
                     35)
        await asyncio.sleep(0.3)
        
        # Step 3: ODI 생성
        add_progress(task_id, "odi_gen", "📄 ODI 파일 생성 중...", 45)
        await asyncio.sleep(0.3)
        
        import re
        dataset_names = set()
        for lbl in parsed["body"].get("data_labels", []):
            m = re.search(r'<([^:]+):([^>]+)>', lbl.get("text", ""))
            if m:
                dataset_names.add(m.group(1))
        
        if not dataset_names:
            dataset_names = {"TR_VIEW"}
        
        # 단일 데이터셋으로 통합 (첫 번째 데이터셋 기준)
        main_dataset = list(dataset_names)[0]
        
        # 기존 ODI 참조 복사 방식
        ref_odi = get_reference_odi_path()
        odi_data = generate_odi(
            odi_name=odi_ref,
            dataset_names=[main_dataset],
            source_odi_path=ref_odi,
        )
        
        odi_path = save_file(odi_data, r_number, "odi")
        add_progress(task_id, "odi_done", 
                     f"✅ ODI 생성 완료: {odi_filename} ({len(odi_data)} bytes)",
                     60)
        await asyncio.sleep(0.3)
        
        # Step 4: OZR 생성
        add_progress(task_id, "ozr_gen", "🔧 OZR 리포트 파일 생성 중...", 70)
        await asyncio.sleep(0.5)
        
        # 파싱 결과를 OZR 설정으로 변환
        parsed["odi_ref_name"] = odi_ref
        parsed["odi_filename"] = odi_filename
        ozr_data = generate_ozr(parsed)
        
        ozr_path = save_file(ozr_data, r_number, "ozr")
        add_progress(task_id, "ozr_done",
                     f"✅ OZR 생성 완료: {ozr_filename} ({len(ozr_data)} bytes)",
                     90)
        await asyncio.sleep(0.3)
        
        # Step 5: 완료
        add_progress(task_id, "complete",
                     f"🎉 생성 완료!\n"
                     f"📁 {ozr_filename} ({round(len(ozr_data)/1024, 1)} KB)\n"
                     f"📁 {odi_filename} ({round(len(odi_data)/1024, 1)} KB)\n"
                     f"📂 저장 위치: {REPORT_DIR}",
                     100, status="completed")
        
    except FileExistsError as e:
        add_progress(task_id, "error", f"❌ 오류: {str(e)}", 0, status="error")
    except Exception as e:
        add_progress(task_id, "error", f"❌ 생성 실패: {str(e)}", 0, status="error")
    finally:
        # 임시 파일 삭제
        try:
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file {xlsx_path}: {e}")




def _build_footer_labels(parsed: dict) -> list:
    """풋터 영역 라벨 정보 구성"""
    footer_labels = []
    for label in parsed.get("footer", {}).get("labels", []):
        footer_labels.append({
            "text": label.get("text", ""),
            "left": label.get("left", 0),
            "top": label.get("top", 0),
            "width": label.get("width", 100),
            "height": label.get("height", 20),
        })
    return footer_labels


@app.get("/api/progress/{task_id}")
async def progress_stream(task_id: str):
    """SSE로 진행상태를 스트리밍합니다."""
    async def event_generator():
        last_index = 0
        timeout_count = 0
        max_timeout = 120  # 최대 120초 대기
        
        while timeout_count < max_timeout:
            if task_id in progress_store:
                entries = progress_store[task_id]
                while last_index < len(entries):
                    entry = entries[last_index]
                    data = json.dumps(entry, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    last_index += 1
                    
                    # 완료 또는 에러면 종료
                    if entry["status"] in ("completed", "error"):
                        return
            
            await asyncio.sleep(0.3)
            timeout_count += 0.3
        
        # 타임아웃
        yield f'data: {{"step":"timeout","message":"⏰ 타임아웃","percent":0,"status":"error"}}\n\n'
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/api/reports/{filename}/preview")
async def get_report_preview(filename: str):
    """
    생성된 OZR 파일의 레포트 레이아웃 정보를 JSON으로 반환합니다.
    프론트엔드에서 시각적으로 렌더링하기 위한 데이터.
    """
    import re as regex
    
    filepath = os.path.join(REPORT_DIR, filename)
    if not os.path.exists(filepath) or not filename.lower().endswith('.ozr'):
        raise HTTPException(status_code=404, detail="OZR 파일을 찾을 수 없습니다.")
    
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        xml_str = data[24:].decode('utf-8', errors='replace')
        
        # OZREPORT 속성 추출
        m = regex.search(r'<OZREPORT\s([^>]+)>', xml_str)
        paper_width = 842
        paper_height = 595
        left_margin = 20
        top_margin = 15
        if m:
            attrs = m.group(1)
            for k, v in regex.findall(r'(\w+)="([^"]*)"', attrs):
                if k == "PAPERWIDTH": paper_width = float(v)
                elif k == "PAPERHEIGHT": paper_height = float(v)
                elif k == "LEFTMARGIN": left_margin = float(v)
                elif k == "TOPMARGIN": top_margin = float(v)
        
        # 밴드 정보 추출
        bands = []
        
        # PageHeaderBand
        for m in regex.finditer(r'<OZBAND\s([^>]*BANDTYPE="1"[^>]*)>(.*?)</OZBAND>', xml_str, regex.DOTALL):
            attrs = m.group(1)
            content = m.group(2)
            band_info = _parse_band_attrs(attrs, "PageHeader")
            band_info["labels"] = _parse_labels(content)
            bands.append(band_info)
        
        # DataBand
        for m in regex.finditer(r'<OZDATABAND\s([^>]*)>(.*?)</OZDATABAND>', xml_str, regex.DOTALL):
            attrs = m.group(1)
            content = m.group(2)
            band_info = _parse_band_attrs(attrs, "DataBand")
            band_info["table"] = _parse_table(content)
            bands.append(band_info)
        
        # PageFooterBand
        for m in regex.finditer(r'<OZBAND\s([^>]*BANDTYPE="9"[^>]*)>(.*?)</OZBAND>', xml_str, regex.DOTALL):
            attrs = m.group(1)
            content = m.group(2)
            band_info = _parse_band_attrs(attrs, "PageFooter")
            band_info["labels"] = _parse_labels(content)
            bands.append(band_info)
        
        return JSONResponse(content={
            "filename": filename,
            "paper_width": paper_width,
            "paper_height": paper_height,
            "left_margin": left_margin,
            "top_margin": top_margin,
            "bands": bands,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _parse_band_attrs(attrs: str, band_type: str) -> dict:
    """밴드 속성 파싱"""
    import re as regex
    info = {"type": band_type, "left": 0, "top": 0, "width": 800, "height": 100}
    for k, v in regex.findall(r'(\w+)="([^"]*)"', attrs):
        if k == "WIDTH": info["width"] = float(v)
        elif k == "HEIGHT": info["height"] = float(v)
        elif k == "LEFT": info["left"] = float(v)
        elif k == "TOP": info["top"] = float(v)
    return info


def _parse_labels(content: str) -> list:
    """OZTABLELABEL/ONESHAPE 라벨 파싱"""
    import re as regex
    labels = []
    for m in regex.finditer(r'<(?:OZTABLELABEL|ONESHAPE)\s([^>]*)>([^<]*)</(?:OZTABLELABEL|ONESHAPE)>', content):
        attrs = m.group(1)
        text = m.group(2).strip()
        label = {"text": text, "left": 0, "top": 0, "width": 100, "height": 20, "fontSize": 10, "bold": False, "align": "left", "bgColor": ""}
        for k, v in regex.findall(r'(\w+)="([^"]*)"', attrs):
            if k == "LEFT": label["left"] = float(v)
            elif k == "TOP": label["top"] = float(v)
            elif k == "WIDTH": label["width"] = float(v)
            elif k == "HEIGHT": label["height"] = float(v)
            elif k == "FONTSIZE": label["fontSize"] = float(v)
            elif k == "FONTSTYLE": label["bold"] = v == "1"
            elif k == "HALIGN":
                label["align"] = {"0": "left", "1": "center", "2": "right"}.get(v, "left")
            elif k == "BGCOLOR" and v != "-1":
                label["bgColor"] = v
            elif k == "DRAWLEFT" and v == "1":
                label["has_border"] = True
        if text or label.get("bgColor"):
            labels.append(label)
    return labels


def _parse_table(content: str) -> dict:
    """OZTABLE 내부의 타이틀/값 라벨 파싱"""
    import re as regex
    table = {"titles": [], "columns": []}
    
    # 타이틀 라벨 (OZTTLABEL)
    for m in regex.finditer(r'<OZTTLABEL\s([^>]*)>([^<]*)</OZTTLABEL>', content):
        attrs = m.group(1)
        text = m.group(2).strip()
        col = {"text": text, "left": 0, "top": 0, "width": 100, "height": 22, "align": "center"}
        for k, v in regex.findall(r'(\w+)="([^"]*)"', attrs):
            if k == "LEFT": col["left"] = float(v)
            elif k == "TOP": col["top"] = float(v)
            elif k == "WIDTH": col["width"] = float(v)
            elif k == "HEIGHT": col["height"] = float(v)
            elif k == "HALIGN":
                col["align"] = {"0": "left", "1": "center", "2": "right"}.get(v, "left")
            elif k == "BGCOLOR" and v != "-1":
                col["bgColor"] = v
            elif k == "DRAWLEFT" and v == "1":
                col["has_border"] = True
        table["titles"].append(col)
    
    # 값 라벨 (OZGROUPLABEL) 
    for m in regex.finditer(r'<OZGROUPLABEL\s([^>]*)/?>', content):
        attrs = m.group(1)
        col = {"field": "", "left": 0, "top": 0, "width": 100, "height": 20, "align": "left"}
        for k, v in regex.findall(r'(\w+)="([^"]*)"', attrs):
            if k == "LEFT": col["left"] = float(v)
            elif k == "TOP": col["top"] = float(v)
            elif k == "WIDTH": col["width"] = float(v)
            elif k == "HEIGHT": col["height"] = float(v)
            elif k == "COLNAME": col["field"] = v
            elif k == "HALIGN":
                col["align"] = {"0": "left", "1": "center", "2": "right"}.get(v, "left")
            elif k == "DRAWLEFT" and v == "1":
                col["has_border"] = True
        table["columns"].append(col)
    
    return table


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  OZ Report Generator Server")
    print("  http://localhost:8088")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8088)

