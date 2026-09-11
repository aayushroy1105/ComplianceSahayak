import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionListItem } from '../../api/types';

const UserDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [recentInspections, setRecentInspections] = useState<InspectionListItem[]>([]);
  const [totalInspections, setTotalInspections] = useState<number>(0);
  const [compliantCount, setCompliantCount] = useState<number>(0);
  const [nonCompliantCount, setNonCompliantCount] = useState<number>(0);
  const [inconclusiveCount, setInconclusiveCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const recentRes = await inspectionsApi.getInspections({ page: 1, page_size: 5, scope: 'user' });
        setRecentInspections(recentRes.items);
        setTotalInspections(recentRes.pagination.total_items);

        const [compRes, nonCompRes, inconcRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT', scope: 'user' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT', scope: 'user' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE', scope: 'user' })
        ]);

        setCompliantCount(compRes.pagination.total_items);
        setNonCompliantCount(nonCompRes.pagination.total_items);
        setInconclusiveCount(inconcRes.pagination.total_items);
        setErrorMsg(null);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setErrorMsg('Failed to load dashboard metrics.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const compPct = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const nonCompPct = totalInspections > 0 ? ((nonCompliantCount / totalInspections) * 100).toFixed(1) : '0.0';

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-slate-300 border-t-slate-800 rounded-full animate-spin"></div>
          <p className="text-sm font-medium text-slate-500">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="bg-red-50 text-red-600 p-6 rounded-lg text-sm border border-red-200 font-medium text-center">
        {errorMsg}
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full pb-10">
      {/* Top Workspace Context & Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-4">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">User Portal</span>
            <span className="text-slate-300">•</span>
            <span className="font-mono text-[10px] text-slate-500">Overview</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mt-1 tracking-tight">User Compliance Workspace</h1>
          <p className="text-sm text-slate-500 mt-2 max-w-2xl leading-relaxed">
            Upload packaging images for automated legal metrology compliance verification and review batch results.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
          <button 
            className="group flex items-center gap-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg hover:bg-slate-800 transition-colors shadow-sm focus:outline-none" 
            type="button"
            onClick={() => navigate('/app/user/scan/new')}
          >
            <Icon name="add" className="text-[18px] transition-transform group-hover:rotate-90" />
            <span className="text-sm font-semibold">+ Start New Package Scan</span>
          </button>
        </div>
      </div>

      {/* Metric Matrix Panel */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 my-4">
        {/* Stat 1: Total Scans */}
        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Total Scans</span>
            <span className="p-1.5 rounded-lg bg-slate-50 border border-slate-100 text-slate-500 flex items-center justify-center">
              <Icon name="document_scanner" className="text-[18px]" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-slate-900">{totalInspections}</span>
            <span className="font-mono text-[10px] text-slate-500 font-semibold">Total Scans</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-medium">
            All time
          </div>
        </div>
        
        {/* Stat 2: Compliant */}
        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Compliant</span>
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-50 border border-emerald-100 text-emerald-700 text-[10px] font-bold tracking-wide uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span> Verified
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-slate-900">{compliantCount}</span>
            <span className="font-mono text-[10px] text-emerald-600 font-semibold">{compPct}% Pass Rate</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-medium">Compliant scans</div>
        </div>
        
        {/* Stat 3: Non-Compliant */}
        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Non-Compliant</span>
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-rose-50 border border-rose-100 text-rose-700 text-[10px] font-bold tracking-wide uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span> Flagged
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-rose-600">{nonCompliantCount}</span>
            <span className="font-mono text-[10px] text-rose-600 font-semibold">{nonCompPct}% Deficit</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-medium">Discrepancies flagged</div>
        </div>
        
        {/* Stat 4: Review Required */}
        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Review Required</span>
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-50 border border-amber-100 text-amber-700 text-[10px] font-bold tracking-wide uppercase">
              <Icon name="warning" className="text-[12px]" /> Ambiguity
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-slate-900">{inconclusiveCount}</span>
            <span className="font-mono text-[10px] text-amber-600 font-semibold">Needs User Review</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-medium">Review recommended</div>
        </div>
      </div>

      {/* Central Work Area: Upload Drag & Scan Zone */}
      <div className="my-2 bg-white border border-slate-200/80 rounded-xl p-6 lg:p-8 shadow-[0_1px_3px_rgba(0,0,0,0.04)] relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-slate-100/50 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex flex-col lg:flex-row items-center justify-between gap-8 relative z-10">
          <div className="flex flex-col max-w-xl text-center lg:text-left items-center lg:items-start">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-slate-50 border border-slate-100 text-slate-700 font-mono text-[11px] mb-3 font-semibold">
              <Icon name="center_focus_strong" className="text-[14px] text-slate-500" />
              <span>Legal Metrology (Packaged Commodities) Rules Verification</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">
              Ready to check a new product label?
            </h2>
            <p className="text-sm text-slate-500 mt-2 leading-relaxed">
              Automated optical analysis assists in identifying packaging declarations for review.
            </p>
            {/* Drop target / trigger */}
            <div className="mt-6 w-full flex flex-col sm:flex-row items-center gap-4">
              <button 
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 shadow-sm transition-all focus:outline-none" 
                type="button"
                onClick={() => navigate('/app/user/scan/new')}
              >
                <Icon name="cloud_upload" className="text-[20px]" />
                <span>Upload &amp; Scan Package &rarr;</span>
              </button>
              <div className="flex items-center gap-1.5 text-slate-500 font-mono text-[11px] font-semibold">
                <Icon name="verified" className="text-[16px]" />
                <span>Supports JPG, PNG, TIFF up to 25MB</span>
              </div>
            </div>
          </div>
          
          {/* Interactive Drop Frame Preview Box */}
          <div 
            className="w-full lg:w-96 flex flex-col items-center justify-center p-8 rounded-xl bg-slate-50 border-2 border-dashed border-slate-200 text-center cursor-pointer transition-colors hover:bg-slate-100 group"
            onClick={() => navigate('/app/user/scan/new')}
          >
            <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center text-slate-400 group-hover:scale-105 group-hover:text-slate-600 transition-all shadow-sm border border-slate-100">
              <Icon name="photo_camera_front" className="text-[32px]" />
            </div>
            <span className="text-sm font-bold text-slate-900 mt-4">Drag &amp; drop package image</span>
            <span className="text-xs text-slate-500 mt-1">or browse system storage</span>
            <div className="flex flex-wrap justify-center items-center gap-2 mt-4 font-mono text-[10px] text-slate-500 font-medium">
              <span className="px-2 py-0.5 rounded bg-white border border-slate-200 shadow-sm">Front PDP</span>
              <span className="px-2 py-0.5 rounded bg-white border border-slate-200 shadow-sm">Nutritional Table</span>
              <span className="px-2 py-0.5 rounded bg-white border border-slate-200 shadow-sm">MRP Panel</span>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Content Split: Recent Scans List vs Guidance Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-4">
        {/* Left Column: Recent Scan Results (8 Cols) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="flex items-center justify-between pb-1">
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-slate-900 tracking-tight">Recent Scan Results</span>
              <span className="font-mono text-[10px] px-2 py-0.5 bg-slate-100 border border-slate-200 rounded text-slate-600 font-semibold">Active Batch</span>
            </div>
            <button 
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 transition-colors"
              onClick={() => navigate('/app/user/scan')}
            >
              <span>View Full Scan History ({totalInspections})</span>
              <Icon name="arrow_forward" className="text-[16px]" />
            </button>
          </div>
          
          {recentInspections.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-sm text-slate-500">
              No recent scans found. Start by uploading a package image.
            </div>
          ) : (
            recentInspections.map((insp) => (
              <div 
                key={insp.id}
                className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer group" 
                onClick={() => navigate(`/app/user/reports/${insp.id}`)}
              >
                <div className="flex items-start gap-4 min-w-0">
                  <div className="w-16 h-16 rounded-lg bg-slate-100 shrink-0 overflow-hidden flex items-center justify-center relative border border-slate-200">
                    <Icon name="photo" className="text-[24px] text-slate-400" />
                    <div className="absolute bottom-1 right-1 p-0.5 rounded bg-white/90 text-slate-600 shadow-sm">
                      <Icon name="search" className="text-[12px]" />
                    </div>
                  </div>
                  <div className="flex flex-col min-w-0">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500 font-semibold">User Portal</span>
                      <span className="text-slate-300">•</span>
                      <span className="font-mono text-[10px] text-slate-500 font-semibold">Overview</span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900 mt-1 truncate group-hover:text-slate-700 transition-colors">
                      {insp.product_name_ai || insp.inspection_code || 'Unknown Product'}
                    </h3>
                    <p className={`text-xs mt-1 flex items-center gap-1.5 font-medium leading-snug ${
                      insp.compliance_status === 'COMPLIANT' ? 'text-emerald-700' :
                      insp.compliance_status === 'NON_COMPLIANT' ? 'text-rose-600' : 'text-amber-600'
                    }`}>
                      <Icon 
                        name={
                          insp.compliance_status === 'COMPLIANT' ? 'check_circle' :
                          insp.compliance_status === 'NON_COMPLIANT' ? 'error' : 'visibility_off'
                        } 
                        className="text-[14px]" 
                      />
                      {insp.compliance_status === 'COMPLIANT' ? 'All mandatory declarations verified' :
                       insp.compliance_status === 'NON_COMPLIANT' ? `${insp.violation_count} violations detected` :
                       'Inconclusive review required'}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mt-2 text-slate-500 font-mono text-[10px]">
                      <span className="flex items-center gap-1">
                        <Icon name="schedule" className="text-[13px]" /> 
                        {insp.inspection_date ? new Date(insp.inspection_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </span>
                      <span className="text-slate-300 hidden sm:inline">•</span>
                      <span>Batch #{insp.inspection_code?.split('-').pop() || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                  <button 
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors focus:outline-none" 
                    type="button"
                  >
                    <span>View Report</span>
                    <Icon name="arrow_forward" className="text-[14px]" />
                  </button>
                </div>
              </div>
            ))
          )}
          
        </div>
        
        {/* Right Column: Institutional Guidance & System Checklist (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          {/* Guidance Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
            <div className="flex items-center gap-2 pb-2">
              <Icon name="info" className="text-[20px] text-slate-500" />
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">How Compliance Checks Work</h3>
            </div>
            <p className="text-xs text-slate-600 mb-4 leading-relaxed">
              Automated optical analysis assists in identifying packaging declarations for review across three standardized phases.
            </p>
            <div className="flex flex-col gap-4 relative">
              {/* Step 1 */}
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white font-mono text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                  1
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-900">Upload Clear Photos</span>
                  <span className="text-xs text-slate-500 mt-1 leading-relaxed">
                    Capture the Principal Display Panel (PDP), manufacturer address box, and price markings under uniform light.
                  </span>
                </div>
              </div>
              {/* Step 2 */}
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white font-mono text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                  2
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-900">Calibrated OCR Extraction</span>
                  <span className="text-xs text-slate-500 mt-1 leading-relaxed">
                    Optical analysis reads packaging declarations and measures numeral sizing for review.
                  </span>
                </div>
              </div>
              {/* Step 3 */}
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white font-mono text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                  3
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-900">Rule Engine Verification</span>
                  <span className="text-xs text-slate-500 mt-1 leading-relaxed">
                    Rule engine checks extracted declarations against applicable packaging standards.
                  </span>
                </div>
              </div>
            </div>
            
            <div className="mt-6 p-4 rounded-lg bg-slate-50 border border-slate-200 flex flex-col gap-2">
              <span className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
                <Icon name="fact_check" className="text-[16px] text-emerald-600" />
                Statutory Declarations Checked
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-[10px] text-slate-600 mt-2 font-medium">
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Name &amp; Address</span>
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Net Quantity (g/ml)</span>
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Month &amp; Year of Pkg</span>
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Maximum Retail Price</span>
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Consumer Helpline</span>
                <span className="flex items-center gap-1"><span className="text-slate-400">•</span> Country of Origin</span>
              </div>
            </div>
          </div>
          
          {/* Quick Upload Tips Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Inspection Quality Tips</span>
            <h4 className="text-lg font-bold text-slate-900 mt-1">Prevent Optical Ambiguity</h4>
            <ul className="mt-3 space-y-3 text-xs text-slate-600">
              <li className="flex items-start gap-2.5">
                <Icon name="wb_sunny" className="text-[16px] text-slate-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">Avoid strong direct flash on reflective foil pouches to prevent MRP washout.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <Icon name="crop" className="text-[16px] text-slate-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">Ensure the entire product silhouette is visible for accurate PDP area ratio measurement.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <Icon name="straighten" className="text-[16px] text-slate-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">Hold packaging parallel to camera lens to eliminate perspective angle distortion.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
