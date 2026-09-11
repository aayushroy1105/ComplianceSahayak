import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import SecureImage from "../../components/ui/SecureImage";
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionDetailResponse } from '../../api/types';

const UserReportView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<InspectionDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchReport = async () => {
      try {
        setIsLoading(true);
        const data = await inspectionsApi.getInspection(id);
        setReport(data);
      } catch (err) {
        console.error('Failed to fetch inspection report:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReport();
  }, [id]);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.15, 1.6));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.15, 0.85));
  const handleResetZoom = () => setZoomLevel(1);

  const handleDownloadReport = async () => {
    if (!id || !report) return;
    try {
      setIsDownloading(true);
      const res = await fetch(`http://localhost:8000/api/v1/inspections/${id}/report/download`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `Report_${report.inspection_code || id}.md`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error('Failed to download report:', err);
      alert('Unable to download report file from server.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleShareReport = async () => {
    if (!id) return;
    try {
      setIsSharing(true);
      const res = await inspectionsApi.shareReport(id);
      window.prompt("Shareable link generated! Anyone with this link can view the report.", res.share_url);
    } catch (err) {
      console.error('Failed to share report:', err);
      alert('Failed to generate share link.');
    } finally {
      setIsSharing(false);
    }
  };

  const mappedDeclarations = report?.declarations?.length 
    ? report.declarations.map((dec, idx) => ({
        id: String(idx + 1),
        checkpoint: dec.field_name ? dec.field_name.replace(/_/g, ' ').replace(/\w\S*/g, (txt: string) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()) : 'Unknown',
        rule: 'N/A', // Rule mapping typically resides in violations
        extracted: dec.raw_value || 'Not extracted',
        standard: 'Standard verification',
        confidence: dec.confidence ? `${(dec.confidence * 100).toFixed(1)}%` : 'N/A',
        status: dec.extraction_status || 'UNKNOWN'
      }))
    : [];

  const mappedViolations = report?.violations || [];
  const primaryImage = report?.images && report.images.length > activeImageIndex ? report.images[activeImageIndex] : (report?.images && report.images.length > 0 ? report.images[0] : null);
  const imageUrl = primaryImage ? `http://localhost:8000/api/v1/inspections/${id}/images/${primaryImage.id}/file` : null;

  if (isLoading) {
    return (
      <div className="flex-1 p-6 flex flex-col items-center justify-center min-h-[60vh] text-slate-500">
        <Icon name="sync" className="text-4xl animate-spin mb-4" />
        <p className="text-lg font-medium">Loading report...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="flex-1 p-6 flex flex-col items-center justify-center min-h-[60vh] text-slate-500">
        <Icon name="error_outline" className="text-4xl mb-4" />
        <p className="text-lg font-medium">Report not found</p>
        <button onClick={() => navigate(-1)} className="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full pb-10">
      {/* Top Context Navigation & Institutional Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-4">
        <nav aria-label="Breadcrumbs" className="flex items-center gap-2 text-slate-500 font-mono text-[10px] font-medium">
          <button className="hover:text-slate-900 transition-colors" onClick={() => navigate('/app/user/scan')} type="button">Scan History</button>
          <span className="text-slate-300">/</span>
          <span className="text-slate-900 text-[11px] font-bold">{report.inspection_code || id}</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-900 text-[11px] font-bold text-slate-900">Compliance Report</span>
        </nav>
        <div className="flex items-center gap-2">
          <button 
            className="inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 text-slate-700 text-xs font-bold rounded-md shadow-sm transition-all focus:outline-none hover:bg-slate-50 cursor-pointer" 
            type="button"
            onClick={handleShareReport}
            disabled={isSharing}
            title="Generate a secure share link for this report"
          >
            <Icon name="share" className="text-[16px]" />
            <span>{isSharing ? 'Sharing...' : 'Share Report'}</span>
          </button>
          <button 
            className="inline-flex items-center gap-2 px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-md shadow-sm transition-all focus:outline-none cursor-pointer" 
            type="button"
            onClick={handleDownloadReport}
            disabled={isDownloading}
            title="Download full statutory compliance report"
          >
            <Icon name="file_download" className="text-[16px]" />
            <span>{isDownloading ? 'Downloading...' : 'Download Report (.md)'}</span>
          </button>
        </div>
      </div>

      {/* Primary Report Header Dossier Block */}
      <div className="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-[9px] px-2 py-0.5 bg-slate-100 border border-slate-200 text-slate-600 font-bold rounded">DOSSIER #{report.inspection_code}</span>
              <span className="font-mono text-[9px] px-2 py-0.5 bg-slate-50 border border-slate-100 text-slate-500 rounded font-medium">Rule 6 LM(PC) Rules 2011</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Compliance Report: {report.product_name_ai || 'Unknown Product'}</h1>
            <p className="text-sm text-slate-500 mt-2 leading-relaxed">
              Category: <strong className="text-slate-900 font-bold">{report.product_category_ai || 'N/A'}</strong> &bull; Scanned: <span className="text-slate-900">{report.inspection_date ? new Date(report.inspection_date).toLocaleString() : 'N/A'}</span>
            </p>
          </div>
          <div className="flex items-center gap-4 self-start lg:self-center">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Processing</span>
              <span className="font-mono text-[11px] text-slate-900 font-medium">{report.processing_status}</span>
            </div>
            <div className="h-8 w-px bg-slate-200"></div>
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Review Status</span>
              <span className={`font-mono text-[11px] font-bold ${report.review_required ? 'text-rose-600' : 'text-emerald-600'}`}>{report.review_status}</span>
            </div>
          </div>
        </div>

        {/* Overall Result Flag Banner */}
        <div className={`border rounded-lg p-4 mt-2 flex flex-col md:flex-row md:items-center justify-between gap-4 ${report.compliance_status === 'NON_COMPLIANT' ? 'bg-rose-50 border-rose-100' : report.compliance_status === 'COMPLIANT' ? 'bg-emerald-50 border-emerald-100' : 'bg-amber-50 border-amber-100'}`}>
          <div className="flex items-start gap-3">
            <div className={`w-8 h-8 rounded-full text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5 ${report.compliance_status === 'NON_COMPLIANT' ? 'bg-rose-600' : report.compliance_status === 'COMPLIANT' ? 'bg-emerald-600' : 'bg-amber-600'}`}>
              <Icon name="rule" className="text-[18px]" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs font-bold uppercase tracking-wider ${report.compliance_status === 'NON_COMPLIANT' ? 'text-rose-700' : report.compliance_status === 'COMPLIANT' ? 'text-emerald-700' : 'text-amber-700'}`}>STATUS: {report.compliance_status || 'PENDING'}</span>
                {report.compliance_status === 'NON_COMPLIANT' && (
                  <span className="font-mono text-[9px] px-2 bg-rose-100 border border-rose-200 text-rose-700 rounded font-bold py-0.5">Rule Discrepancy Found</span>
                )}
              </div>
              <p className={`text-sm font-medium ${report.compliance_status === 'NON_COMPLIANT' ? 'text-rose-800' : report.compliance_status === 'COMPLIANT' ? 'text-emerald-800' : 'text-amber-800'}`}>
                {report.compliance_status === 'NON_COMPLIANT' ? `${mappedViolations.length} discrepancies detected against packaging rules.` : report.compliance_status === 'COMPLIANT' ? 'Product is fully compliant with packaging rules.' : 'Pending review or inconclusive analysis.'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
            {mappedViolations.length > 0 && <span className="font-mono text-[10px] text-rose-700 font-bold bg-rose-100/50 border border-rose-200 px-3 py-1.5 rounded">{mappedViolations.length} Rule Discrepancies</span>}
            {report.review_required && <span className="font-mono text-[10px] text-amber-700 font-bold bg-amber-100/50 border border-amber-200 px-3 py-1.5 rounded">Manual Review Required</span>}
          </div>
        </div>
      </div>

      {/* Metric Snapshot Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Evaluated Mandates</span>
          <div className="flex items-baseline justify-between mt-3">
            <span className="text-3xl font-bold text-slate-900">{mappedDeclarations.length}</span>
            <span className="font-mono text-[10px] text-slate-500 font-medium">Statutory Rules</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-4 overflow-hidden">
            <div className="bg-slate-900 h-full w-full"></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Compliant Declarations</span>
          <div className="flex items-baseline justify-between mt-3">
            <span className="text-3xl font-bold text-emerald-700">{mappedDeclarations.filter(d => d.status === 'COMPLIANT').length}</span>
            <span className="font-mono text-[10px] text-emerald-600 font-bold">Pass</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-4 overflow-hidden">
            <div className="bg-emerald-500 h-full w-[100%]"></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Statutory Deficits</span>
          <div className="flex items-baseline justify-between mt-3">
            <span className="text-3xl font-bold text-rose-600">{mappedViolations.length}</span>
            <span className="font-mono text-[10px] text-rose-600 font-bold">Violations</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-4 overflow-hidden">
            <div className="bg-rose-600 h-full w-[100%]"></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Manual Review Required</span>
          <div className="flex items-baseline justify-between mt-3">
            <span className="text-3xl font-bold text-amber-600">{report.review_required ? 'Yes' : 'No'}</span>
            <span className="font-mono text-[10px] text-amber-600 font-bold">Visual check</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-2 leading-snug">
            {report.review_reason || 'Automated analysis was inconclusive. The provided evidence is insufficient for a definitive compliance status.'}
          </p>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-4 overflow-hidden">
            <div className="bg-amber-500 h-full w-[100%]"></div>
          </div>
        </div>
      </div>

      {/* Primary Split Architecture: Evidence Visualizer (Left) vs Itemized Findings (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start mb-6">
        
        {/* LEFT PANE: Calibrated Evidence Visualizer (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 overflow-hidden flex flex-col">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="view_in_ar" className="text-[18px] text-slate-900" />
              <span className="text-sm font-bold text-slate-900">Calibrated Packaging Scan</span>
            </div>
            <div className="flex items-center gap-1">
              <button 
                className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-900 focus:outline-none transition-colors" 
                onClick={handleZoomIn}
                title="Zoom In" 
                type="button"
              >
                <Icon name="zoom_in" className="text-[18px]" />
              </button>
              <button 
                className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-900 focus:outline-none transition-colors" 
                onClick={handleZoomOut}
                title="Zoom Out" 
                type="button"
              >
                <Icon name="zoom_out" className="text-[18px]" />
              </button>
              <button 
                className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-900 focus:outline-none transition-colors" 
                onClick={handleResetZoom}
                title="Reset View" 
                type="button"
              >
                <Icon name="refresh" className="text-[18px]" />
              </button>
            </div>
          </div>
          
          {/* Scanned Package Stage with Real Packaging Asset */}
          <div className="relative bg-slate-100 p-4 flex items-center justify-center min-h-[460px] overflow-hidden border-b border-slate-200/50">
            <div 
              className="relative max-w-sm w-full bg-white rounded shadow-md overflow-hidden transition-transform duration-200 ease-out" 
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
            >
              {/* Packaging Visual Preview */}
              {imageUrl ? (
                <SecureImage 
                  src={imageUrl} 
                  alt="Scanned Package" 
                  className="w-full h-[400px] object-contain bg-slate-900" 
                />
              ) : (
                <div className="w-full h-[400px] bg-slate-200 flex flex-col items-center justify-center text-slate-400">
                  <Icon name="image_not_supported" className="text-[48px] mb-2" />
                  <span className="text-sm font-medium">Image preview not available</span>
                </div>
              )}
              
              {/* Grid Overlay lines for Metrology inspection calibration */}
              <div className="absolute inset-0 pointer-events-none opacity-[0.15]" style={{ backgroundImage: 'linear-gradient(to right, #94a3b8 1px, transparent 1px), linear-gradient(to bottom, #94a3b8 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
            </div>
          </div>
          
          {/* Thumbnails for Multi-Angle */}
          {report?.images && report.images.length > 1 && (
            <div className="bg-slate-100 border-b border-slate-200 p-3 flex items-center justify-center gap-3 overflow-x-auto shadow-inner">
              {report.images.map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => {
                    setActiveImageIndex(idx);
                    setZoomLevel(1);
                  }}
                  className={`relative flex flex-col items-center justify-center p-1.5 rounded-md border-2 transition-all focus:outline-none ${activeImageIndex === idx ? 'border-slate-900 bg-white shadow-sm' : 'border-transparent hover:bg-slate-200'}`}
                  title={`View ${img.image_type} angle`}
                  type="button"
                >
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${activeImageIndex === idx ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-600'}`}>
                    {img.image_type || 'OTHER'}
                  </span>
                </button>
              ))}
            </div>
          )}
          
          {/* Evidence Calibration Telemetry */}
          <div className="p-4 bg-white grid grid-cols-3 gap-2 text-center border-b border-slate-200/50">
            <div className="bg-slate-50 border border-slate-100 p-2 rounded-lg">
              <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Asset Type</span>
              <span className="font-mono text-[11px] text-slate-900 font-bold">{primaryImage?.image_type || 'FRONT'} Angle</span>
            </div>
            <div className="bg-slate-50 border border-slate-100 p-2 rounded-lg">
              <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">File Payload</span>
              <span className="font-mono text-[11px] text-slate-900 font-bold">{primaryImage ? `${Math.round(primaryImage.file_size / 1024)} KB` : 'N/A'}</span>
            </div>
            <div className="bg-slate-50 border border-slate-100 p-2 rounded-lg">
              <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">MIME Type</span>
              <span className="font-mono text-[11px] text-slate-900 font-bold">{primaryImage?.mime_type || 'image/jpeg'}</span>
            </div>
          </div>
          <div className="p-3 bg-slate-50 flex items-center justify-between text-slate-500 font-mono text-[10px] font-medium">
            <span>Dossier UID: {report.inspection_code || id}</span>
            {imageUrl && (
              <button 
                onClick={async () => {
                  try {
                    const res = await fetch(imageUrl, {
                      credentials: 'include'
                    });
                    if (!res.ok) throw new Error('Fetch failed');
                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    window.open(url, '_blank');
                  } catch (err) {
                    console.error(err);
                  }
                }}
                className="text-slate-700 hover:text-slate-900 font-bold flex items-center gap-1 hover:underline cursor-pointer"
              >
                <span>View Full Size Asset</span>
                <Icon name="open_in_new" className="text-[14px]" />
              </button>
            )}
          </div>
        </div>

        {/* RIGHT PANE: Itemized Compliance Findings (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          
          {mappedViolations.length === 0 ? (
            <div className="bg-white rounded-xl p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col items-center justify-center text-center text-slate-500 h-full min-h-[400px]">
              <Icon name="verified" className="text-4xl text-emerald-500 mb-3" />
              <p className="font-medium text-slate-900">No violations detected</p>
              <p className="text-sm mt-1">This product meets all evaluated statutory declarations.</p>
            </div>
          ) : (
            mappedViolations.map((violation, i) => (
              <div key={violation.id || i} className="bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-rose-50 border border-rose-100 text-rose-700 text-[10px] font-bold tracking-wide uppercase">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                      NON_COMPLIANT
                    </span>
                    <span className="font-mono text-[10px] text-slate-500 font-medium">{violation.rule_id || 'Unknown Rule'}</span>
                  </div>
                  <span className="font-mono text-[10px] bg-slate-50 border border-slate-200 px-2 py-0.5 rounded text-slate-600 font-bold">Violation ID: {violation.violation_code}</span>
                </div>
                <h2 className="text-base font-bold text-slate-900 mt-1">DETERMINISTIC RULE FINDING: {violation.rule_id}</h2>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">{violation.description}</p>
                <div className="bg-slate-50 border border-slate-100 rounded-lg p-4 my-4 flex flex-col gap-3 font-mono text-[11px] font-medium">
                  {violation.corrective_actions?.map((action, aidx) => (
                    <div key={aidx} className="flex items-center justify-between">
                      <span className="text-slate-500">Corrective Action {aidx + 1}:</span>
                      <span className="text-amber-700 font-bold flex items-center gap-1.5">
                        <Icon name="build" className="text-[14px]" />
                        {action.action_text}
                      </span>
                    </div>
                  ))}
                  {(!violation.corrective_actions || violation.corrective_actions.length === 0) && (
                    <span className="text-slate-500">No corrective actions logged.</span>
                  )}
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <span className="font-mono text-[10px] text-slate-500 font-medium">Confidence: {violation.confidence ? (violation.confidence * 100).toFixed(1) + '%' : 'N/A'}</span>
                  <button type="button" className="px-4 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-md shadow-sm transition-colors focus:outline-none">
                    View Evidence
                  </button>
                </div>
              </div>
            ))
          )}
          
        </div>
      </div>

      {/* Section 3: Verified Declarations Matrix (8 Checkpoints) */}
      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 overflow-hidden mb-8">
        <div className="p-4 sm:p-6 lg:p-8 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Evaluated Declarations Matrix</h2>
            <p className="text-sm text-slate-500 mt-1 leading-relaxed">Automated extraction and rule evaluation results for packaging declarations.</p>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-center">
            <span className="font-mono text-[10px] px-3 py-1.5 bg-slate-50 border border-slate-200 text-slate-600 font-bold rounded-md">Filter: 8 Total</span>
          </div>
        </div>
        
        {/* Accessible Data Table */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="py-3 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider">Statutory Checkpoint</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Extracted Value / Reading</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Regulatory Standard</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">OCR Confidence</th>
                <th className="py-3 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Verification Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {mappedDeclarations.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 text-xs">No declarations extracted for this report.</td>
                </tr>
              ) : mappedDeclarations.map((item) => {
                const isNonCompliant = item.status === 'NON_COMPLIANT';
                const isReview = item.status === 'REVIEW REQUIRED' || item.status === 'INCONCLUSIVE';

                return (
                  <tr key={item.id} className={`${isNonCompliant ? 'bg-rose-50/50 hover:bg-rose-50' : isReview ? 'bg-amber-50/50 hover:bg-amber-50' : 'hover:bg-slate-50/80'} transition-colors`}>
                    <td className="py-4 px-6 align-top">
                      <span className={`text-sm font-bold block mb-1 ${isNonCompliant ? 'text-rose-700' : isReview ? 'text-amber-700' : 'text-slate-900'}`}>{item.id}. {item.checkpoint}</span>
                      <span className="font-mono text-[10px] text-slate-500 font-medium">{item.rule}</span>
                    </td>
                    <td className="py-4 px-4 align-top">
                      <span className={`${isNonCompliant || isReview ? 'font-bold text-slate-900' : 'text-slate-700'}`}>{item.extracted}</span>
                    </td>
                    <td className={`py-4 px-4 align-top text-xs ${isNonCompliant ? 'text-rose-600 font-medium' : isReview ? 'text-amber-600 font-medium' : 'text-slate-500'}`}>
                      {item.standard}
                    </td>
                    <td className={`py-4 px-4 align-top font-mono text-[11px] ${isNonCompliant || isReview ? 'font-bold ' + (isNonCompliant ? 'text-slate-900' : 'text-amber-700') : 'text-slate-600 font-medium'}`}>
                      {item.confidence}
                    </td>
                    <td className="py-4 px-6 align-top text-right whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded border text-[10px] font-bold tracking-wide uppercase ${
                        isNonCompliant ? 'bg-rose-50 text-rose-700 border-rose-200' :
                        isReview ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}>
                        {isNonCompliant ? (
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                        ) : isReview ? (
                          <Icon name="warning" className="text-[13px]" />
                        ) : (
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                        )}
                        {item.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {/* Table Footnote & Statutory Audit Seal */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Icon name="policy" className="text-[18px] text-slate-900" />
            <span className="font-medium">Standardized automated evaluation according to LM(PC) Statutory Guidelines.</span>
          </div>
          <div className="font-mono text-[10px] font-bold text-slate-400">
            Report Generated: {report.inspection_date ? new Date(report.inspection_date).toLocaleString() : new Date().toLocaleString()}
          </div>
        </div>
      </div>

      {/* Bottom Regulatory Notice / Institutional Boundaries */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg flex items-start gap-3">
        <Icon name="verified_user" className="text-slate-400 text-[20px] shrink-0 mt-0.5" />
        <p className="text-xs text-slate-600 leading-relaxed">
          <strong className="text-slate-900 font-bold">ComplianceSahayak Advisory Notice:</strong> This report reflects automated analysis from optical extraction and rule evaluation models for quality review and packaging compliance assistance. It does not constitute official statutory adjudication.
        </p>
      </div>

    </div>
  );
};

export default UserReportView;
