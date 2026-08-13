'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

const API_BASE = 'http://localhost:8088';

export default function Home() {
  const [currentStep, setCurrentStep] = useState(1); // 1: Upload, 2: Preview, 3: Generate
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [preview, setPreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progressEntries, setProgressEntries] = useState([]);
  const [progressPercent, setProgressPercent] = useState(0);
  const [generateStatus, setGenerateStatus] = useState(null); // null, 'processing', 'completed', 'error'
  const [fileInfo, setFileInfo] = useState(null);
  const [generatedFilename, setGeneratedFilename] = useState(null);
  const [reportLayout, setReportLayout] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUploadingOzr, setIsUploadingOzr] = useState(false);
  const fileInputRef = useRef(null);
  const progressRef = useRef(null);
  const ozrFileInputRef = useRef(null);

  // 파일 목록 조회
  useEffect(() => {
    fetch(`${API_BASE}/api/files`)
      .then(res => res.json())
      .then(data => setFileInfo(data))
      .catch(() => {});
  }, []);

  // 파일 선택 핸들러
  const handleFileSelect = useCallback((selectedFile) => {
    if (!selectedFile) return;
    if (!selectedFile.name.match(/\.(xlsx|xls)$/i)) {
      alert('XLSX 파일만 업로드 가능합니다.');
      return;
    }
    setFile(selectedFile);
    setPreview(null);
    setCurrentStep(1);
    setGenerateStatus(null);
    setProgressEntries([]);
    setGeneratedFilename(null);
  }, []);

  // 드래그 앤 드롭
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  // 파일 삭제
  const removeFile = () => {
    setFile(null);
    setPreview(null);
    setCurrentStep(1);
    setGenerateStatus(null);
    setProgressEntries([]);
    setGeneratedFilename(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // XLSX 분석 (미리보기)
  const analyzeFile = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch(`${API_BASE}/api/preview`, {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '분석 실패');
      }
      
      const data = await res.json();
      setPreview(data);
      setCurrentStep(2);
    } catch (err) {
      alert(`분석 오류: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // OZR/ODI 생성
  const generateReport = async () => {
    if (!file) return;
    setIsGenerating(true);
    setGenerateStatus('processing');
    setProgressEntries([]);
    setProgressPercent(0);
    setCurrentStep(3);
    setGeneratedFilename(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '생성 실패');
      }
      
      const data = await res.json();
      const taskId = data.task_id;
      
      // SSE로 진행상태 구독
      const eventSource = new EventSource(`${API_BASE}/api/progress/${taskId}`);
      
      eventSource.onmessage = (event) => {
        try {
          const entry = JSON.parse(event.data);
          setProgressEntries(prev => [...prev, entry]);
          setProgressPercent(entry.percent);
          
          if (entry.status === 'completed') {
            setGenerateStatus('completed');
            setIsGenerating(false);
            if (entry.message.match(/PLA0501_R\d+\.ozr/)) {
               const match = entry.message.match(/PLA0501_R\d+\.ozr/);
               if (match) setGeneratedFilename(match[0]);
            }
            eventSource.close();
            // 파일 목록 새로고침
            fetch(`${API_BASE}/api/files`)
              .then(r => r.json())
              .then(d => setFileInfo(d))
              .catch(() => {});
          } else if (entry.status === 'error') {
            setGenerateStatus('error');
            setIsGenerating(false);
            eventSource.close();
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };
      
      eventSource.onerror = () => {
        setGenerateStatus('error');
        setIsGenerating(false);
        eventSource.close();
      };
      
    } catch (err) {
      alert(`생성 오류: ${err.message}`);
      setGenerateStatus('error');
      setIsGenerating(false);
    }
  };

  // OZR 시각 미리보기
  const viewOzrPreview = async () => {
    if (!generatedFilename) return;
    try {
      const res = await fetch(`${API_BASE}/api/reports/${generatedFilename}/preview`);
      if (!res.ok) throw new Error('OZR 파일을 불러오지 못했습니다.');
      const data = await res.json();
      setReportLayout(data);
      setIsModalOpen(true);
    } catch (err) {
      alert(err.message);
    }
  };

  // OZR 다이렉트 뷰어 (업로드)
  const handleOzrDirectUpload = async (file) => {
    if (!file) return;
    if (!file.name.match(/\.ozr$/i)) {
      alert('OZR 파일만 업로드 가능합니다.');
      return;
    }
    
    setIsUploadingOzr(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch(`${API_BASE}/api/preview-ozr`, {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'OZR 파싱 실패');
      }
      
      const data = await res.json();
      setGeneratedFilename(file.name);
      setReportLayout(data);
      setIsModalOpen(true);
    } catch (err) {
      alert(`OZR 뷰어 오류: ${err.message}`);
    } finally {
      setIsUploadingOzr(false);
      if (ozrFileInputRef.current) ozrFileInputRef.current.value = '';
    }
  };

  // 새로 만들기
  const resetAll = () => {
    setFile(null);
    setPreview(null);
    setCurrentStep(1);
    setGenerateStatus(null);
    setProgressEntries([]);
    setProgressPercent(0);
    setIsGenerating(false);
    setGeneratedFilename(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // 진행 표시 자동 스크롤
  useEffect(() => {
    if (progressRef.current) {
      progressRef.current.scrollTop = progressRef.current.scrollHeight;
    }
  }, [progressEntries]);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <div className="app-logo-icon">📊</div>
          <div>
            <h1 className="app-title">OZ Report Generator</h1>
            <p className="app-subtitle">XLSX → OZR/ODI 자동 변환기</p>
          </div>
        </div>
      </header>

      {/* Steps Indicator */}
      <div className="steps-container">
        <div className={`step-dot ${currentStep >= 1 ? (currentStep > 1 ? 'completed' : 'active') : ''}`}>
          <span className="step-number">{currentStep > 1 ? '✓' : '1'}</span>
          파일 업로드
        </div>
        <div className={`step-connector ${currentStep > 1 ? 'completed' : ''}`} />
        <div className={`step-dot ${currentStep >= 2 ? (currentStep > 2 ? 'completed' : 'active') : ''}`}>
          <span className="step-number">{currentStep > 2 ? '✓' : '2'}</span>
          분석 미리보기
        </div>
        <div className={`step-connector ${currentStep > 2 ? 'completed' : ''}`} />
        <div className={`step-dot ${currentStep >= 3 ? 'active' : ''} ${generateStatus === 'completed' ? 'completed' : ''}`}>
          <span className="step-number">{generateStatus === 'completed' ? '✓' : '3'}</span>
          생성 완료
        </div>
      </div>

      {/* File Info Banner */}
      {fileInfo && (
        <div className="info-banner info-banner-blue" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            📁 현재 PLA0501 시리즈: OZR {fileInfo.total_ozr}개, ODI {fileInfo.total_odi}개
            &nbsp;|&nbsp; 다음 번호: <strong>{fileInfo.next_ozr_filename}</strong>
          </div>
          <div>
            <button 
              className="btn btn-secondary" 
              style={{ padding: '6px 12px', fontSize: '13px', margin: 0 }}
              onClick={() => ozrFileInputRef.current?.click()}
              disabled={isUploadingOzr}
            >
              {isUploadingOzr ? '열기 중...' : '🔍 OZR 원본 열기 (비교용)'}
            </button>
            <input
              ref={ozrFileInputRef}
              type="file"
              accept=".ozr"
              style={{ display: 'none' }}
              onChange={(e) => handleOzrDirectUpload(e.target.files[0])}
            />
          </div>
        </div>
      )}

      {/* Step 1: Upload */}
      {currentStep === 1 && (
        <div className="card">
          <h2 className="card-title">📤 엑셀 파일 업로드</h2>
          <p className="card-desc">고객 요청 엑셀 파일(.xlsx)을 업로드하면 자동으로 헤더/바디/풋터를 분석합니다.</p>

          <div
            className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="upload-icon">📎</div>
            <p className="upload-text">여기에 XLSX 파일을 끌어다 놓거나 클릭하세요</p>
            <p className="upload-hint">지원 형식: .xlsx, .xls</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              className="upload-input"
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
          </div>

          {file && (
            <>
              <div className="file-info">
                <span className="file-info-icon">📊</span>
                <div>
                  <div className="file-info-name">{file.name}</div>
                  <div className="file-info-size">{(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <button className="file-remove" onClick={removeFile}>✕</button>
              </div>

              <div className="btn-group">
                <button
                  className="btn btn-primary"
                  onClick={analyzeFile}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <span className="spinner" />
                      분석 중...
                    </>
                  ) : (
                    <>🔍 파일 분석하기</>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Step 2: Preview */}
      {currentStep === 2 && preview && (
        <div className="card">
          <h2 className="card-title">📋 분석 결과 미리보기</h2>
          <p className="card-desc">엑셀 파일에서 추출된 리포트 구조입니다. 확인 후 생성 버튼을 누르세요.</p>

          <div className="preview-section">
            <div className="preview-grid">
              <div className="preview-item">
                <div className="preview-item-value">{preview.summary.header_labels_count}</div>
                <div className="preview-item-label">헤더 라벨</div>
              </div>
              <div className="preview-item">
                <div className="preview-item-value">{preview.summary.body_title_labels_count || 0}</div>
                <div className="preview-item-label">테이블 컬럼</div>
              </div>
              <div className="preview-item">
                <div className="preview-item-value">{preview.summary.body_data_labels_count || 0}</div>
                <div className="preview-item-label">데이터 영역 라벨</div>
              </div>
              <div className="preview-item">
                <div className="preview-item-value">{preview.summary.footer_labels_count}</div>
                <div className="preview-item-label">풋터 라벨</div>
              </div>
            </div>

          </div>

          <div className="info-banner" style={{ marginTop: '20px', marginBottom: 0 }}>
            ⚡ 생성될 파일: <strong>PLA0501_R{String(preview.next_r_number).padStart(2, '0')}.ozr</strong> / <strong>.odi</strong>
          </div>

          <div className="btn-group">
            <button className="btn btn-secondary" onClick={() => setCurrentStep(1)}>
              ← 다시 업로드
            </button>
            <button
              className="btn btn-primary"
              onClick={generateReport}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner" />
                  생성 중...
                </>
              ) : (
                <>🚀 OZR/ODI 생성하기</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Progress & Result */}
      {currentStep === 3 && (
        <div className={`card ${generateStatus === 'completed' ? 'result-card' : ''}`}>
          <h2 className="card-title">
            {generateStatus === 'completed' ? '✅ 생성 완료!' : 
             generateStatus === 'error' ? '❌ 오류 발생' : 
             '⚙️ 생성 진행 중...'}
          </h2>
          <p className="card-desc">
            {generateStatus === 'completed' 
              ? 'OZR/ODI 파일이 성공적으로 생성되었습니다.'
              : generateStatus === 'error'
              ? '파일 생성 중 오류가 발생했습니다.'
              : 'XLSX 분석 → OZR 생성 → ODI 생성 순서로 진행됩니다.'}
          </p>

          <div className="progress-container">
            {/* Progress Bar */}
            <div className={`progress-percent ${generateStatus === 'completed' ? 'completed' : ''}`}>
              {progressPercent}%
            </div>
            <div className="progress-bar-track">
              <div
                className={`progress-bar-fill ${generateStatus === 'completed' ? 'completed' : ''}`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Progress Steps */}
            <div className="progress-steps" ref={progressRef}>
              {progressEntries.map((entry, idx) => {
                const isLatest = idx === progressEntries.length - 1;
                const stepClass = entry.status === 'error' ? 'error-step' :
                                  entry.status === 'completed' ? 'completed-step' :
                                  isLatest ? 'latest' : '';
                return (
                  <div key={idx} className={`progress-step ${stepClass}`}>
                    {entry.status === 'completed' ? '🎉' :
                     entry.status === 'error' ? '❌' :
                     isLatest && generateStatus === 'processing' ? <span className="spinner" /> :
                     '✅'}
                    <span style={{ whiteSpace: 'pre-line' }}>{entry.message}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Result Actions */}
          {(generateStatus === 'completed' || generateStatus === 'error') && (
            <div className="btn-group">
              {generateStatus === 'completed' && generatedFilename && (
                <button className="btn btn-secondary" onClick={viewOzrPreview}>
                  👀 레포트 미리보기
                </button>
              )}
              <button className="btn btn-primary" onClick={resetAll}>
                🔄 새 리포트 생성
              </button>
            </div>
          )}
        </div>
      )}

      {/* Report Visual Preview Modal */}
      {isModalOpen && reportLayout && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content modal-wide" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📄 {generatedFilename} 레포트 미리보기</h3>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="report-preview-wrapper">
                <div
                  className="report-paper"
                  style={{
                    width: reportLayout.paper_width,
                    height: reportLayout.paper_height,
                    paddingLeft: reportLayout.left_margin,
                    paddingTop: reportLayout.top_margin,
                  }}
                >
                  {reportLayout.bands.map((band, bi) => (
                    <div
                      key={bi}
                      className={`report-band report-band-${band.type.toLowerCase()}`}
                      style={{
                        position: 'absolute',
                        left: reportLayout.left_margin + (band.left || 0),
                        top: reportLayout.top_margin + (band.top || 0),
                        width: band.width,
                        height: band.height,
                      }}
                    >
                      {/* Header/Footer 라벨 */}
                      {band.labels && band.labels.map((lbl, li) => (
                        <div
                          key={li}
                          className="report-label"
                          style={{
                            position: 'absolute',
                            left: lbl.left,
                            top: lbl.top,
                            width: lbl.width,
                            height: lbl.height,
                            fontSize: Math.max(lbl.fontSize * 0.9, 7),
                            fontWeight: lbl.bold ? 700 : 400,
                            textAlign: lbl.align,
                            background: lbl.bgColor ? `rgba(100,100,200,0.15)` : 'transparent',
                            border: lbl.has_border ? '1px solid #000' : 'none',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: lbl.align === 'center' ? 'center' : lbl.align === 'right' ? 'flex-end' : 'flex-start',
                            padding: '0 2px',
                            overflow: 'hidden',
                          }}
                        >
                          {lbl.text}
                        </div>
                      ))}

                      {/* DataBand 테이블 */}
                      {band.table && (
                        <>
                          {/* Table Titles */}
                          {band.table.titles.map((t, ti) => (
                            <div
                              key={`th-${ti}`}
                              className="report-label"
                              style={{
                                position: 'absolute',
                                left: t.left,
                                top: t.top,
                                width: t.width,
                                height: t.height,
                                fontSize: 10,
                                fontWeight: 700,
                                textAlign: t.align,
                                background: t.bgColor ? `#e2e8f0` : 'transparent',
                                border: t.has_border ? '1px solid #000' : 'none',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: t.align === 'center' ? 'center' : t.align === 'right' ? 'flex-end' : 'flex-start',
                                padding: '0 2px',
                                overflow: 'hidden',
                              }}
                            >
                              {t.text}
                            </div>
                          ))}
                          
                          {/* Table Columns (Values) */}
                          {band.table.columns.map((c, ci) => (
                            <div
                              key={`tc-${ci}`}
                              className="report-label"
                              style={{
                                position: 'absolute',
                                left: c.left,
                                top: c.top,
                                width: c.width,
                                height: c.height,
                                fontSize: 10,
                                fontWeight: 400,
                                textAlign: c.align,
                                background: 'transparent',
                                border: c.has_border ? '1px solid #000' : 'none',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: c.align === 'center' ? 'center' : c.align === 'right' ? 'flex-end' : 'flex-start',
                                padding: '0 2px',
                                overflow: 'hidden',
                              }}
                            >
                              <span className="report-field-placeholder">{c.field || `COL${ci+1}`}</span>
                            </div>
                          ))}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
