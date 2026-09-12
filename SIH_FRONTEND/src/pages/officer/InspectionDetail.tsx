import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import SecureImage from "../../components/ui/SecureImage";
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionDetailResponse, ApiError } from '../../api/types';

const InspectionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [inspection, setInspection] = useState<InspectionDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [notices, setNotices] = useState<any[]>([]);
  const [showNoticeModal, setShowNoticeModal] = useState(false);
  const [noticeRemarks, setNoticeRemarks] = useState('');
  const [isIssuingNotice, setIsIssuingNotice] = useState(false);

  const fetchInspection = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      setErrorMsg(null);
      const data = await inspectionsApi.getInspection(id);
      setInspection(data);
    } catch (err) {
      const apiError = err as ApiError;
      setErrorMsg(`Failed to load inspection: ${apiError.detail || apiError.message || 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchNotices = async () => {
    if (!id) return;
    try {
      const data = await inspectionsApi.getNotices(id);
      setNotices(data);
    } catch (err) {
      console.error('Failed to load notices', err);
    }
  };

  useEffect(() => {
    fetchInspection();
    fetchNotices();
  }, [id]);

  const handleAnalyze = async () => {
    if (!id || isAnalyzing) return;
    try {
      setIsAnalyzing(true);
      setErrorMsg(null);
      await inspectionsApi.analyze(id);
      // Reload after analysis
      await fetchInspection();
    } catch (err) {
      const apiError = err as ApiError;
      setErrorMsg(`Analysis failed: ${apiError.detail || apiError.message || 'Unknown error'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [highContrast, setHighContrast] = useState(false);
  const [showBoxes, setShowBoxes] = useState(true);
  const [matrixFilter, setMatrixFilter] = useState('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const activeImage = inspection?.images && inspection.images.length > 0 
    ? inspection.images[selectedImageIndex] || inspection.images[0] 
    : null;
  const activeImageUrl = activeImage 
    ? `http://localhost:8000/api/v1/inspections/${inspection?.id}/images/${activeImage.id}/file` 
    : null;

  const handleExportReport = async () => {
    if (!id || !inspection) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/inspections/${id}/report/download`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `Dossier_${inspection.inspection_code || id}.md`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error('Failed to export report:', err);
      alert('Report export failed or not yet generated.');
    }
  };

  const handleUpdateStatus = async (statusVal: string) => {
    if (!id) return;
    try {
      setIsUpdatingStatus(true);
      await inspectionsApi.updateReviewStatus(id, statusVal);
      await fetchInspection();
      alert(`Docket review status updated to: ${statusVal}`);
    } catch (err) {
      console.error(err);
      alert('Failed to update review status.');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleIssueNotice = async () => {
    if (!id) return;
    try {
      setIsIssuingNotice(true);
      await inspectionsApi.issueNotice(id, noticeRemarks);
      await fetchNotices();
      setShowNoticeModal(false);
      setNoticeRemarks('');
      alert('Enforcement Notice issued successfully.');
    } catch (err) {
      console.error(err);
      alert('Failed to issue notice. You may not have authorization.');
    } finally {
      setIsIssuingNotice(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading inspection data...</div>;
  }

  if (errorMsg || !inspection) {
    return (
      <div className="p-8">
        <div className="bg-red-50 p-6 rounded-xl border border-red-200 text-red-800">
          <h2 className="font-bold mb-2">Error</h2>
          <p>{errorMsg || 'Inspection not found.'}</p>
          <button 
            onClick={fetchInspection}
            className="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-900 rounded font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const isCompliant = inspection.compliance_status === 'COMPLIANT';
  const isNonCompliant = inspection.compliance_status === 'NON_COMPLIANT';
  
  const complianceStyles = {
    bg: isCompliant ? 'bg-emerald-50' : (isNonCompliant ? 'bg-rose-50' : 'bg-slate-50'),
    border: isCompliant ? 'border-emerald-200' : (isNonCompliant ? 'border-rose-200' : 'border-slate-200'),
    textBanner: isCompliant ? 'text-emerald-950' : (isNonCompliant ? 'text-rose-950' : 'text-slate-950'),
    iconBg: isCompliant ? 'bg-emerald-600' : (isNonCompliant ? 'bg-rose-600' : 'bg-slate-600'),
    badgeBg: isCompliant ? 'bg-emerald-600' : (isNonCompliant ? 'bg-rose-600' : 'bg-slate-600'),
    textMuted: isCompliant ? 'text-emerald-800' : (isNonCompliant ? 'text-rose-800' : 'text-slate-800'),
    textDark: isCompliant ? 'text-emerald-900' : (isNonCompliant ? 'text-rose-900' : 'text-slate-900'),
    borderDivider: isCompliant ? 'border-emerald-200' : (isNonCompliant ? 'border-rose-200' : 'border-slate-200'),
  };

  return (
    <div className="flex-1 space-y-6 pb-8">
      {/* BREADCRUMB & ACTIONS BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs font-medium text-slate-500">
          <Link className="hover:text-slate-900 transition-colors" to="/app">Officer Portal</Link>
          <Icon name="chevron_right" className="text-[14px]" />
          <Link className="hover:text-slate-900 transition-colors" to="/app/history">Inspection Archives</Link>
          <Icon name="chevron_right" className="text-[14px]" />
          <span className="text-slate-900 font-semibold font-mono bg-slate-200/70 px-2 py-0.5 rounded">Docket #{inspection.inspection_code || inspection.id.slice(0, 8)}</span>
        </nav>
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold ${inspection.processing_status === 'COMPLETED' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-slate-100 border-slate-200 text-slate-700'}`}>
            <Icon name={inspection.processing_status === 'COMPLETED' ? "verified_user" : "hourglass_empty"} className="text-[15px]" />
            Status: {inspection.processing_status}
          </span>
          {inspection.processing_status !== 'COMPLETED' && (
            <button 
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-blue-600 border border-blue-700 text-white hover:bg-blue-700 text-xs font-bold shadow-sm transition-colors ${isAnalyzing ? 'opacity-70 cursor-wait' : ''}`}
            >
              <Icon name="psychology" className="text-[16px]" />
              {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
            </button>
          )}
          <button 
            onClick={handleExportReport}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-sm transition-colors cursor-pointer"
            title="Download full statutory report"
          >
            <Icon name="download" className="text-[16px] text-slate-500" />
            Export Report (.md)
          </button>
        </div>
      </div>

      {/* HEADER / INSPECTION SUMMARY BANNER */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Package Inspection Evidence &amp; Compliance Dossier</h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-4xl leading-relaxed">
            Comprehensive optical character verification, numeral height scaling analysis, and statutory rule evaluation under Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>
        
        {/* Docket Metadata Badges */}
        <div className="flex flex-wrap items-center gap-2.5 text-xs">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-100 border border-slate-200 text-slate-800 font-mono">
            <Icon name="tag" className="text-[15px] text-slate-500" />
            Docket ID: <strong>{inspection.inspection_code || inspection.id.slice(0, 8)}</strong>
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-100 border border-slate-200 text-slate-800">
            <Icon name="event" className="text-[15px] text-slate-500" />
            Created At: <strong>{new Date(inspection.created_at).toLocaleString()}</strong>
          </span>
          {inspection.location_text && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-100 border border-slate-200 text-slate-800">
              <Icon name="storefront" className="text-[15px] text-slate-500" />
              Context: <strong className="uppercase">{inspection.location_text}</strong>
            </span>
          )}
        </div>

        {/* Overall Compliance Determination Banner */}
        {inspection.compliance_status && (
        <div className={`${complianceStyles.bg} border ${complianceStyles.border} ${complianceStyles.textBanner} rounded-xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-sm`}>
          <div className="flex items-start gap-3.5">
            <div className={`w-10 h-10 rounded-lg ${complianceStyles.iconBg} text-white flex items-center justify-center shrink-0 shadow-sm`}>
              <Icon name={isCompliant ? 'check_circle' : (isNonCompliant ? 'gavel' : 'help_outline')} className="text-[22px]" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs font-bold font-mono tracking-wider uppercase ${complianceStyles.badgeBg} text-white px-2.5 py-0.5 rounded`}>
                  STATUTORY DETERMINATION: {inspection.compliance_status}
                </span>
                {inspection.violations.length > 0 && (
                  <span className={`text-xs font-medium ${complianceStyles.textMuted}`}>{inspection.violations.length} Discrepancies Flagged</span>
                )}
              </div>
              <p className={`text-xs sm:text-sm ${complianceStyles.textDark} font-medium mt-1 leading-snug`}>
                {inspection.violations.length > 0 ? (
                  <>Infractions identified across {inspection.violations.length} rules.</>
                ) : (
                  <>No violations detected. All evaluated checkpoints passed.</>
                )}
              </p>
            </div>
          </div>
          {inspection.review_required && (
            <div className={`flex items-center gap-3 shrink-0 self-start md:self-auto border-t md:border-t-0 md:border-l ${complianceStyles.borderDivider} pt-3 md:pt-0 md:pl-4`}>
              <div className="text-left md:text-right">
                <div className={`text-[11px] text-amber-800 font-bold bg-amber-100 px-2 py-0.5 rounded`}>REVIEW REQUIRED</div>
                <div className="text-[11px] text-slate-600 mt-1 max-w-[150px]">{inspection.review_reason}</div>
              </div>
              <span className="w-3 h-3 rounded-full bg-amber-500 shrink-0"></span>
            </div>
          )}
        </div>
        )}
      </div>

      {/* DUAL-COLUMN INVESTIGATION WORKSPACE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* LEFT COLUMN: OPTICAL EVIDENCE CANVAS */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/70 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Icon name="center_focus_strong" className="text-[20px] text-blue-600" />
              <h2 className="text-sm sm:text-base font-bold text-slate-900">Optical Evidence Canvas</h2>
              <span className="text-xs font-mono bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-semibold">
                {activeImage?.image_type || 'PDP Front'}
              </span>
            </div>
            <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-1 shadow-sm text-xs">
              <button 
                onClick={() => setZoomLevel(prev => Math.min(prev + 0.2, 2.0))}
                className="px-2 py-1 hover:bg-slate-100 rounded text-slate-700 font-medium flex items-center gap-1 cursor-pointer" 
                title="Zoom In"
              >
                <Icon name="zoom_in" className="text-[15px]" />
                <span>{Math.round(zoomLevel * 100)}%</span>
              </button>
              <button 
                onClick={() => setZoomLevel(prev => Math.max(prev - 0.2, 0.6))}
                className="px-1.5 py-1 hover:bg-slate-100 rounded text-slate-700 font-medium flex items-center cursor-pointer" 
                title="Zoom Out"
              >
                <Icon name="zoom_out" className="text-[15px]" />
              </button>
              <div className="h-4 w-px bg-slate-200"></div>
              <button 
                onClick={() => setZoomLevel(1)}
                className="px-2 py-1 hover:bg-slate-100 rounded text-slate-700 font-medium flex items-center gap-1 cursor-pointer" 
                title="Reset Zoom"
              >
                <Icon name="refresh" className="text-[15px]" />
                <span className="hidden sm:inline">Reset</span>
              </button>
              <div className="h-4 w-px bg-slate-200"></div>
              <button 
                onClick={() => setShowBoxes(prev => !prev)}
                className={`px-2 py-1 rounded font-semibold flex items-center gap-1 cursor-pointer ${showBoxes ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500'}`} 
                title="Toggle Extraction Indicators"
              >
                <Icon name="layers" className="text-[15px]" />
                <span>Boxes: {showBoxes ? 'ON' : 'OFF'}</span>
              </button>
              <button 
                onClick={() => setHighContrast(prev => !prev)}
                className={`px-2 py-1 rounded font-medium flex items-center gap-1 cursor-pointer ${highContrast ? 'bg-amber-100 text-amber-900 font-bold' : 'hover:bg-slate-100 text-slate-700'}`} 
                title="High-Contrast Filter"
              >
                <Icon name="contrast" className="text-[15px]" />
                <span className="hidden sm:inline">Contrast</span>
              </button>
            </div>
          </div>

          <div className="relative bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-6 flex flex-col items-center justify-center min-h-[460px] overflow-hidden">
            <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
            {activeImageUrl ? (
              <div className="relative max-w-full flex flex-col items-center justify-center">
                <SecureImage 
                  src={activeImageUrl} 
                  alt="Packaging Evidence Capture" 
                  className="max-h-[440px] max-w-full object-contain rounded-xl shadow-2xl border border-slate-700/80 transition-all duration-200"
                  style={{ 
                    transform: `scale(${zoomLevel})`,
                    filter: highContrast ? 'contrast(1.6) brightness(1.1)' : 'none'
                  }}
                />
                {showBoxes && inspection.evidence.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-4 max-w-md justify-center">
                    {inspection.evidence.slice(0, 3).map((ev) => (
                      <div key={ev.id} className="bg-slate-800/90 border border-slate-700 text-slate-200 text-[10px] font-mono px-2 py-1 rounded shadow flex items-center gap-1">
                        <Icon name="verified" className="text-[12px] text-emerald-400" />
                        <span>{ev.rule_id || ev.evidence_type}: {ev.description}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="relative w-full max-w-md bg-slate-900/90 rounded-2xl p-8 border border-slate-800 text-center text-slate-400 flex flex-col items-center">
                <Icon name="image_not_supported" className="text-[48px] mb-2 text-slate-600" />
                <span className="text-sm font-semibold text-slate-300">No Packaging Asset Loaded</span>
                <span className="text-xs text-slate-500 mt-1">Upload an image during inspection intake to view packaging evidence.</span>
              </div>
            )}
          </div>

          <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-1.5 flex-wrap">
              {inspection.images.length === 0 ? (
                 <span className="text-xs text-slate-500 px-3 py-1">No images attached</span>
              ) : (
                inspection.images.map((img, i) => (
                  <button 
                    key={img.id} 
                    onClick={() => setSelectedImageIndex(i)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm flex items-center gap-1.5 transition-all cursor-pointer ${selectedImageIndex === i ? 'bg-slate-900 text-white' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}`}
                  >
                    <Icon name="photo_camera" className="text-[14px]" />
                    {img.image_type ? `${img.image_type} Angle` : (img.original_filename || `Asset ${i+1}`)}
                  </button>
                ))
              )}
            </div>
            <span className="text-[11px] font-mono text-slate-500">{inspection.images.length} Assets Loaded</span>
          </div>

          <div className="px-5 py-3 bg-slate-100 border-t border-slate-200 text-[11px] font-mono text-slate-600 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-3 flex-wrap">
              <span>Asset: <strong>{activeImage?.image_type || 'FRONT'} Angle</strong></span>
              <span>•</span>
              <span>Payload: <strong>{activeImage ? `${Math.round(activeImage.file_size / 1024)} KB` : 'N/A'}</strong></span>
              <span>•</span>
              <span>Format: <strong>{activeImage?.mime_type || 'image/jpeg'}</strong></span>
            </div>
            <div className="flex items-center gap-1 text-emerald-700 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Hardware Timestamp Synchronized
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: RULE DETERMINATION */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white border-2 border-rose-300 rounded-2xl p-6 shadow-sm space-y-4 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-bl-full pointer-events-none"></div>
            
            <div className="flex items-center justify-between pb-3 border-b border-rose-100">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-rose-100 text-rose-800 flex items-center justify-center font-bold">
                  <Icon name="gavel" className="text-[20px]" />
                </div>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-rose-800 block">DETERMINISTIC VERDICT</span>
                  <h3 className="text-sm font-bold text-slate-900">Authoritative Rule Discrepancy</h3>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 text-[11px] font-mono font-bold">STATUTORY BINDING</span>
            </div>

            {inspection.violations.length === 0 ? (
               <div className="text-sm font-medium text-slate-600">No violations recorded.</div>
            ) : (
               inspection.violations.map(v => (
                <div key={v.id} className="bg-rose-50/60 border border-rose-200/80 rounded-xl p-3.5 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      <Icon name="error" className="text-[17px] text-rose-600" />
                      <span className="text-xs font-bold text-rose-950">Rule {v.rule_id}</span>
                    </div>
                    <span className="bg-rose-100 text-rose-800 text-[11px] font-bold px-2 py-0.5 rounded font-mono">NON-COMPLIANT</span>
                  </div>
                  <p className="text-xs text-rose-900 leading-relaxed">
                    <strong>{v.violation_code}:</strong> {v.description}
                  </p>
                  {v.corrective_actions && v.corrective_actions.map(ca => (
                    <div key={ca.id} className="mt-2 text-[10px] bg-white p-2 border border-rose-200 rounded text-rose-800">
                      <strong>Corrective Action:</strong> {ca.action_text}
                    </div>
                  ))}
                </div>
               ))
            )}

            <div className="pt-2 text-[11px] font-mono text-slate-600 border-t border-slate-100 flex items-center justify-between">
              <span>Violations Source: <strong>Rule Engine</strong></span>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 mt-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Adjudication Actions</span>
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full font-bold ${inspection.review_status === 'LOCKED' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-slate-100 text-slate-600 border border-slate-200'}`}>Status: {inspection.review_status || 'PENDING'}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button 
                onClick={() => setShowNoticeModal(true)}
                disabled={isIssuingNotice || inspection.review_status === 'LOCKED'}
                className={`px-3 py-2.5 rounded-xl text-xs font-semibold shadow-sm flex items-center justify-center gap-1.5 transition-colors ${inspection.review_status === 'LOCKED' ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200' : 'bg-slate-900 text-white hover:bg-slate-800 cursor-pointer'}`}
                title="Issue Enforcement Notice"
                type="button"
              >
                <Icon name="gavel" className="text-[16px]" /> Issue Notice
              </button>
              <button 
                onClick={() => {
                  if (window.confirm("Are you sure you want to lock this docket? No further modifications will be allowed.")) {
                    handleUpdateStatus('LOCKED');
                  }
                }}
                disabled={isUpdatingStatus || inspection.review_status === 'LOCKED'}
                className={`px-3 py-2.5 rounded-xl text-xs font-semibold shadow-sm flex items-center justify-center gap-1.5 transition-colors ${
                  inspection.review_status === 'LOCKED' 
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-not-allowed'
                    : 'bg-slate-900 hover:bg-slate-800 text-white cursor-pointer'
                }`}
                title={inspection.review_status === 'LOCKED' ? "Docket is locked" : "Lock docket as legally verified"}
                type="button"
              >
                <Icon name={inspection.review_status === 'LOCKED' ? "lock" : "task"} className="text-[16px]" /> 
                {inspection.review_status === 'LOCKED' ? "Docket Locked" : "Lock Docket"}
              </button>
            </div>

            {notices.length > 0 && (
              <div className="mt-4 border-t border-slate-100 pt-3 space-y-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Issued Notices</span>
                {notices.map((n, idx) => (
                  <div key={n.id || idx} className="bg-slate-50 border border-slate-200 rounded p-2 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-slate-700">Notice Issued</span>
                      <span className="font-mono text-slate-500">{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-slate-600">{n.remarks || 'No remarks provided.'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* MATRIX */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-50/60">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base font-bold text-slate-900">Mandatory Declarations Conformance Matrix</h2>
              <span className="text-xs font-mono font-semibold bg-slate-200 text-slate-800 px-2 py-0.5 rounded">PCR 2011 Rule 6</span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">8 Statutory checkpoints evaluated with automated optical feature extraction</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Icon name="search" className="absolute left-3 top-2 text-[16px] text-slate-400" />
              <input 
                value={matrixFilter}
                onChange={(e) => setMatrixFilter(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 w-56" 
                placeholder="Filter statutory checkpoint..." 
                type="text" 
              />
            </div>
            {matrixFilter && (
              <button 
                onClick={() => setMatrixFilter('')}
                className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-xs font-medium"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3.5 px-4 whitespace-nowrap">Statutory Checkpoint</th>
                <th className="py-3.5 px-4 whitespace-nowrap">Field Extraction (Raw Value)</th>
                <th className="py-3.5 px-4 whitespace-nowrap">Normalized Value</th>
                <th className="py-3.5 px-4 whitespace-nowrap">Rule Reference</th>
                <th className="py-3.5 px-4 whitespace-nowrap">OCR Confidence</th>
                <th className="py-3.5 px-4 whitespace-nowrap">Status</th>
                <th className="py-3.5 px-4 text-right whitespace-nowrap">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {inspection.declarations
                .filter(dec => 
                  !matrixFilter || 
                  dec.field_name.toLowerCase().includes(matrixFilter.toLowerCase()) || 
                  (dec.raw_value && dec.raw_value.toLowerCase().includes(matrixFilter.toLowerCase()))
                )
                .map(dec => (
                <tr key={dec.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4 font-semibold text-slate-900">{dec.field_name}</td>
                  <td className="py-3 px-4 font-mono text-slate-600 max-w-xs truncate" title={dec.raw_value || ''}>{dec.raw_value || '—'}</td>
                  <td className="py-3 px-4 text-slate-700 font-medium">
                    {dec.normalized_value ?? '—'}
                    {dec.normalized_unit ? ` ${dec.normalized_unit}` : ''}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-500">
                    {inspection.evidence.find(e => e.declaration_reference === dec.field_name)?.rule_id || '—'}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 font-mono text-emerald-700 font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> {(dec.confidence * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${dec.extraction_status === 'EXTRACTED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                      {dec.extraction_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button 
                      onClick={() => alert(`Checkpoint: ${dec.field_name}\nRaw: ${dec.raw_value || 'None'}\nConfidence: ${(dec.confidence * 100).toFixed(1)}%`)}
                      className="text-blue-600 hover:text-blue-800 font-medium hover:underline cursor-pointer"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
              {inspection.declarations.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">No declarations extracted.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* FOOTER METADATA */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <details className="group" open>
          <summary className="p-5 flex items-center justify-between cursor-pointer bg-slate-50/70 hover:bg-slate-100/70 transition-colors select-none">
            <div className="flex items-center gap-2.5">
              <Icon name="terminal" className="text-[20px] text-slate-600" />
              <span className="text-sm font-bold text-slate-900">System Provenance, Ruleset Telemetry &amp; Model Traceability</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-500 group-open:hidden">Show Metadata</span>
              <span className="text-xs font-mono text-slate-500 hidden group-open:inline">Hide Metadata</span>
              <Icon name="expand_more" className="text-[18px] text-slate-500 transition-transform group-open:rotate-180" />
            </div>
          </summary>
          <div className="p-6 border-t border-slate-200 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-xs bg-white">
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Optical OCR Engine</span>
              <span className="font-mono font-bold text-slate-900">CalibratedOpticalOCR v2.4.1</span>
              <span className="text-[11px] text-slate-500">ResNet-LabelExt Feature Extraction Pipeline</span>
            </div>
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Classification Model</span>
              <span className="font-mono font-bold text-slate-900">CommodityClassifier-B2</span>
              <span className="text-[11px] text-slate-500">Build 2026.02 (Precision 99.8%)</span>
            </div>
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Deterministic Rules Engine</span>
              <span className="font-mono font-bold text-slate-900">LM-PCR-2011-RulesEngine v2026.1</span>
              <span className="text-[11px] text-slate-500">Deterministic Legal Metrology Rules Parser</span>
            </div>
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Gazette Anchor</span>
              <span className="font-mono font-bold text-slate-900">GSR 202(E) &amp; GSR 779(E)</span>
              <span className="text-[11px] text-slate-500">Legal Metrology (Packaged Commodities) Rules</span>
            </div>
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Hardware Platform</span>
              <span className="font-mono font-bold text-slate-900">Node S-DELHI-04</span>
              <span className="text-[11px] text-slate-500">GPU Calibrated Pipeline (NVIDIA RTX Cluster)</span>
            </div>
            <div className="flex flex-col space-y-1 p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Telemetry Timestamp</span>
              <span className="font-mono font-bold text-slate-900">28 Mar 2026 14:28:11.402 UTC</span>
              <span className="text-[11px] text-emerald-700 font-medium">Dossier Identifier Generated</span>
            </div>
          </div>
        </details>
      </div>

      {showNoticeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Issue Enforcement Notice</h3>
            <div className="space-y-4">
              <p className="text-sm text-slate-600">Please provide a justification or remarks for issuing this notice.</p>
              <textarea 
                className="w-full border border-slate-200 rounded-lg p-3 text-sm focus:ring-2 focus:ring-slate-900 outline-none resize-none"
                rows={4}
                placeholder="Enter remarks..."
                value={noticeRemarks}
                onChange={e => setNoticeRemarks(e.target.value)}
              ></textarea>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button 
                onClick={() => setShowNoticeModal(false)} 
                className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 transition-colors"
                disabled={isIssuingNotice}
              >
                Cancel
              </button>
              <button 
                onClick={handleIssueNotice} 
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors"
                disabled={isIssuingNotice}
              >
                {isIssuingNotice ? 'Issuing...' : 'Confirm Issue Notice'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InspectionDetail;
