import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionListItem } from '../../api/types';

const OfficerDashboard: React.FC = () => {
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
        // Fetch recent list (for pending/recent) and get global total
        const recentRes = await inspectionsApi.getInspections({ page: 1, page_size: 5 });
        setRecentInspections(recentRes.items);
        setTotalInspections(recentRes.pagination.total_items);

        // Fetch counts via total_items from filtered requests
        const [compRes, nonCompRes, inconcRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE' })
        ]);

        setCompliantCount(compRes.pagination.total_items);
        setNonCompliantCount(nonCompRes.pagination.total_items);
        setInconclusiveCount(inconcRes.pagination.total_items);
        setErrorMsg(null);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setErrorMsg('Failed to load dashboard metrics. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const compPct = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const nonCompPct = totalInspections > 0 ? ((nonCompliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const inconcPct = totalInspections > 0 ? ((inconclusiveCount / totalInspections) * 100).toFixed(1) : '0.0';

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
    <>
      {/* PAGE TITLE & TOP ACTIONS */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Officer Compliance Dashboard</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">Operational review queue and verification overview</p>
        </div>
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <button onClick={() => window.location.reload()} className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium shadow-sm transition-colors cursor-pointer">
            <Icon name="refresh" className="text-[16px] text-slate-500 transition-transform" />
            <span>Refresh</span>
          </button>
          <button 
            onClick={() => {
              const csvContent = "data:text/csv;charset=utf-8," 
                + "Metric,Count,Percentage\\n"
                + `Total Inspections,${totalInspections},100%\\n`
                + `Compliant,${compliantCount},${compPct}%\\n`
                + `Non-Compliant,${nonCompliantCount},${nonCompPct}%\\n`
                + `Inconclusive,${inconclusiveCount},${inconcPct}%\\n`;
              const encodedUri = encodeURI(csvContent);
              const link = document.createElement("a");
              link.setAttribute("href", encodedUri);
              link.setAttribute("download", "officer_dashboard_summary.csv");
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }} 
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium cursor-pointer shadow-sm transition-colors" title="Export Dashboard Summary">
            <Icon name="download" className="text-[16px] text-slate-500" />
            <span>Export Summary</span>
          </button>
          <Link className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium shadow-sm transition-colors" to="/app/inspection/new">
            <Icon name="add" className="text-[16px]" />
            <span>New Inspection</span>
          </Link>
        </div>
      </div>

      {/* 4 BALANCED KPI METRIC CARDS */}
      <div className="kpi-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        {/* Card 1: Total Inspections */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Inspections</span>
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
              <Icon name="description" className="text-[18px]" />
            </div>
          </div>
          <div>
            <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{totalInspections}</span>
            <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
              <span>All recorded scans</span>
            </div>
          </div>
        </div>

        {/* Card 2: Non-Compliant */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Non-Compliant</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <Icon name="error" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{nonCompliantCount}</span>
              <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[11px] font-semibold">{nonCompPct}%</span>
            </div>
            <p className="text-xs text-rose-700 font-medium mt-2">Requires officer review</p>
          </div>
        </div>

        {/* Card 3: Review Required */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Review Required</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
              <Icon name="visibility" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{inconclusiveCount}</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[11px] font-semibold">Inconclusive</span>
            </div>
            <p className="text-xs text-amber-700 font-medium mt-2">Awaiting officer adjudication</p>
          </div>
        </div>

        {/* Card 4: Compliant */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Compliant</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <Icon name="check_circle" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{compliantCount}</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-semibold">Verified</span>
            </div>
            <p className="text-xs text-emerald-700 font-medium mt-2">{compPct}% compliance rate</p>
          </div>
        </div>
      </div>

      {/* WORKSPACE COMPOSITION */}
      <div className="desktop-col-layout grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN: PENDING OFFICER REVIEW */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <h2 className="text-sm sm:text-base font-bold text-slate-900">Recent Inspections</h2>
              <span className="px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold font-mono">{recentInspections.length} Items</span>
            </div>
            <div className="inline-flex p-1 bg-slate-200/70 rounded-lg text-xs font-medium text-slate-600 overflow-x-auto">
              <button className="px-3 py-1.5 rounded-md bg-white text-slate-900 font-semibold shadow-sm transition-colors shrink-0">Recent</button>
            </div>
          </div>
          
          <div className="divide-y divide-slate-100">
            {recentInspections.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500">
                No recent inspections found.
              </div>
            ) : (
              recentInspections.map((insp) => (
                <div key={insp.id} className="p-5 hover:bg-slate-50/80 transition-colors">
                  <div className="hidden sm:flex items-center justify-between gap-4">
                    <div className="flex flex-col space-y-1.5 min-w-0 pr-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 shrink-0">
                          {insp.inspection_code}
                        </span>
                        {insp.compliance_status === 'NON_COMPLIANT' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 shrink-0">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                            NON_COMPLIANT
                          </span>
                        )}
                        {insp.compliance_status === 'COMPLIANT' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            COMPLIANT
                          </span>
                        )}
                        {(insp.compliance_status === 'INCONCLUSIVE' || insp.compliance_status === null) && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 shrink-0">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                            {insp.compliance_status || 'PENDING'}
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-slate-900 text-sm leading-snug break-words">
                        {insp.product_name_ai || 'Unknown Product'}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-slate-500 flex-wrap">
                        <span className="text-slate-700 font-medium">{insp.manufacturer_name || 'Unknown Manufacturer'}</span>
                        {insp.violation_count > 0 && (
                          <>
                            <span>•</span>
                            <span className="text-rose-600 font-medium">{insp.violation_count} Violations Detected</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-xs font-mono text-slate-400">
                        {insp.inspection_date ? new Date(insp.inspection_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </span>
                      <Link to={`/app/inspection/${insp.id}`} className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors shadow-sm">
                        <span>View Dossier</span>
                        <Icon name="arrow_forward" className="text-[14px]" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="px-5 py-4 bg-slate-50/80 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
            <span className="text-xs text-slate-500 text-center sm:text-left">Showing latest {recentInspections.length} active items</span>
            <div className="flex items-center gap-2">
              <Link to="/app/history" className="px-3.5 py-1.5 rounded-md bg-white border border-slate-200 text-slate-800 hover:bg-slate-50 text-xs font-semibold shadow-sm">View Full History</Link>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="lg:col-span-4 flex flex-col gap-6 w-full">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900">Compliance Distribution</h3>
              <span className="text-xs font-mono text-slate-500 font-semibold bg-slate-100 px-2 py-0.5 rounded">{totalInspections} Total</span>
            </div>
            <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden flex mb-5 border border-slate-200/70">
              <div className="h-full bg-emerald-500" style={{ width: `${compPct}%` }} title={`Compliant: ${compPct}%`}></div>
              <div className="h-full bg-rose-500" style={{ width: `${nonCompPct}%` }} title={`Non-Compliant: ${nonCompPct}%`}></div>
              <div className="h-full bg-amber-400" style={{ width: `${inconcPct}%` }} title={`Inconclusive: ${inconcPct}%`}></div>
            </div>
            <div className="flex flex-col space-y-3.5">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0"></span>
                  <span className="font-medium text-slate-800">Compliant (Verified)</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-slate-500">{compliantCount} units</span>
                  <span className="font-bold text-emerald-700">{compPct}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shrink-0"></span>
                  <span className="font-medium text-slate-800">Non-Compliant</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-slate-500">{nonCompliantCount} infractions</span>
                  <span className="font-bold text-rose-700">{nonCompPct}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shrink-0"></span>
                  <span className="font-medium text-slate-800">Inconclusive Review</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-slate-500">{inconclusiveCount} manual</span>
                  <span className="font-bold text-amber-700">{inconcPct}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default OfficerDashboard;
