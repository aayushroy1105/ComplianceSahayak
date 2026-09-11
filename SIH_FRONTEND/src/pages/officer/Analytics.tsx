import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';

const Analytics: React.FC = () => {
  const [totalInspections, setTotalInspections] = useState<number>(0);
  const [compliantCount, setCompliantCount] = useState<number>(0);
  const [nonCompliantCount, setNonCompliantCount] = useState<number>(0);
  const [inconclusiveCount, setInconclusiveCount] = useState<number>(0);
  const [recentInspections, setRecentInspections] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setIsLoading(true);
        const [allRes, compRes, nonCompRes, inconcRes, recentRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1 }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE' }),
          inspectionsApi.getInspections({ page: 1, page_size: 5 })
        ]);
        setTotalInspections(allRes.pagination.total_items);
        setCompliantCount(compRes.pagination.total_items);
        setNonCompliantCount(nonCompRes.pagination.total_items);
        setInconclusiveCount(inconcRes.pagination.total_items);
        setRecentInspections(recentRes.items || []);
      } catch (err) {
        console.error('Failed to load metrics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  const exportCSV = () => {
    const headers = ['Inspection Code', 'Product Name', 'Manufacturer', 'Category', 'Date', 'Status', 'Violations'];
    const rows = recentInspections.map(i => [
      i.inspection_code,
      `"${i.product_name_ai || ''}"`,
      `"${i.manufacturer_name || ''}"`,
      `"${i.product_category_ai || ''}"`,
      i.inspection_date || '',
      i.compliance_status || '',
      i.violation_count || 0
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `analytics_summary_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const compPct = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const nonCompPct = totalInspections > 0 ? ((nonCompliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const inconcPct = totalInspections > 0 ? ((inconclusiveCount / totalInspections) * 100).toFixed(1) : '0.0';

  return (
    <div className="flex-1 pb-8 space-y-6 overflow-x-hidden">
      {/* Top Operational Control & Breadcrumb Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 sm:p-6 rounded-xl shadow-sm border border-slate-200">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Compliance &amp; Inspection Analytics</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">Operational review of compliance distribution derived from live inspection data</p>
        </div>
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div className="flex items-center bg-slate-100 rounded-lg p-1 border border-slate-200">
            <button disabled className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 cursor-not-allowed" type="button" title="Date filtering not yet available">
              <Icon name="calendar_today" className="text-[15px]" />
              <span>Date Filter</span>
            </button>
            <button disabled className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 cursor-not-allowed" type="button" title="Commodity filtering not yet available">
              <Icon name="tune" className="text-[15px]" />
              <span>Category Filter</span>
            </button>
          </div>
          <button 
            onClick={exportCSV}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium shadow-sm transition-colors cursor-pointer" 
            type="button"
          >
            <Icon name="file_download" className="text-[16px]" />
            <span>Export Analytics (CSV)</span>
          </button>
        </div>
      </div>

      {/* 4 Canonical KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        {/* Card 1: Total Inspections */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Inspections</span>
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
              <Icon name="inventory_2" className="text-[18px]" />
            </div>
          </div>
          <div>
            <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{isLoading ? '...' : totalInspections}</span>
            <div className="flex items-center gap-2 mt-2 text-xs text-slate-500 flex-wrap">
              <span>All recorded scans</span>
            </div>
          </div>
        </div>

        {/* Card 2: Overall Compliance */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overall Compliance</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <Icon name="verified" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{isLoading ? '...' : `${compPct}%`}</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-semibold border border-emerald-200/60">{compliantCount} Validated</span>
            </div>
          </div>
        </div>

        {/* Card 3: Flagged Deficits */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Flagged Deficits</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <Icon name="error" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{isLoading ? '...' : `${nonCompPct}%`}</span>
              <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[11px] font-semibold border border-rose-200/60">{nonCompliantCount} Notices</span>
            </div>
          </div>
        </div>

        {/* Card 4: Review Required */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Review Required</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
              <Icon name="visibility" className="text-[18px]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{isLoading ? '...' : `${inconcPct}%`}</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[11px] font-semibold border border-amber-200/60">{inconclusiveCount} Pending</span>
            </div>
          </div>
        </div>
      </div>

      {/* Analytical Charts Section */}
      <div className="bg-white p-10 rounded-xl shadow-sm border border-slate-200 text-center flex flex-col items-center justify-center min-h-[300px]">
        <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-4">
          <Icon name="bar_chart" className="text-[24px]" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-1">Advanced Analytics Unavailable</h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto">
          Detailed time-series telemetry and deficit matrix charting are currently unpopulated. 
          Please generate more inspection reports to unlock these operational insights.
        </p>
      </div>



      {/* Audit Activity Summary Table Strip */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Field Inspection Cohort Log</h3>
            <span className="text-[11px] sm:text-xs text-slate-500 font-medium">Systematic record of evaluated dockets during current enforcement rotation</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-slate-500 font-medium">Showing {recentInspections.length} of {totalInspections} instances</span>
            <Link className="inline-flex items-center gap-1 text-xs font-bold text-slate-700 hover:text-slate-900 transition-colors" to="/app/history">
              <span>View All</span>
              <Icon name="arrow_forward" className="text-[14px]" />
            </Link>
          </div>
        </div>
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-white border-b border-slate-200 text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                <th className="py-3 px-5">Docket Identifier</th>
                <th className="py-3 px-5">Commodity Specification</th>
                <th className="py-3 px-5">Manufacturer / Brand</th>
                <th className="py-3 px-5">Inspection Date</th>
                <th className="py-3 px-5">Adjudication Result</th>
                <th className="py-3 px-5 text-right w-32">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700 font-medium">
              {recentInspections.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500">No inspections recorded yet.</td>
                </tr>
              ) : (
                recentInspections.map((insp) => {
                  const isNonCompliant = insp.compliance_status === 'NON_COMPLIANT';
                  const isCompliant = insp.compliance_status === 'COMPLIANT';

                  return (
                    <tr key={insp.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3.5 px-5 font-mono font-bold text-slate-900">{insp.inspection_code}</td>
                      <td className="py-3.5 px-5 font-bold text-slate-800">{insp.product_name_ai || '—'}</td>
                      <td className="py-3.5 px-5 text-slate-600 font-medium">{insp.manufacturer_name || '—'}</td>
                      <td className="py-3.5 px-5 font-mono text-slate-500 text-[11px]">{insp.inspection_date ? new Date(insp.inspection_date).toLocaleDateString() : 'N/A'}</td>
                      <td className="py-3.5 px-5">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                          isNonCompliant ? 'bg-rose-50 text-rose-700 border-rose-200' :
                          isCompliant ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                          'bg-amber-50 text-amber-700 border-amber-200'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            isNonCompliant ? 'bg-rose-500' :
                            isCompliant ? 'bg-emerald-500' :
                            'bg-amber-500'
                          }`}></span>
                          {insp.compliance_status || 'PENDING'}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right">
                        <Link 
                          to={`/app/inspection/${insp.id}`} 
                          className="inline-flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-[11px] font-bold transition-colors shadow-sm cursor-pointer"
                        >
                          <span>View Dossier</span>
                          <Icon name="arrow_forward" className="text-[13px]" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
