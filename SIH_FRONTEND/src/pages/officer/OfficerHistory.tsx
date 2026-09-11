import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionListItem } from '../../api/types';

const OfficerHistory: React.FC = () => {
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [totalInspections, setTotalInspections] = useState<number>(0);
  const [compliantCount, setCompliantCount] = useState<number>(0);
  const [nonCompliantCount, setNonCompliantCount] = useState<number>(0);
  const [inconclusiveCount, setInconclusiveCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const fetchPage = async (page: number, status?: string) => {
    try {
      setIsLoading(true);
      const params: any = { page, page_size: 10 };
      if (status && status !== 'ALL') {
        params.compliance_status = status;
      }
      const res = await inspectionsApi.getInspections(params);
      setInspections(res.items);
      setTotalInspections(res.pagination.total_items);
      setTotalPages(res.pagination.total_pages);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPage(currentPage, statusFilter);
  }, [currentPage, statusFilter]);

  const exportHistoryCSV = () => {
    const headers = ['Docket ID', 'Product', 'Manufacturer', 'Timestamp', 'Status', 'Violations'];
    const rows = inspections.map(i => [
      i.inspection_code,
      `"${i.product_name_ai || ''}"`,
      `"${i.manufacturer_name || ''}"`,
      i.inspection_date || '',
      i.compliance_status || '',
      i.violation_count || 0
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `officer_inspection_history_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredInspections = inspections.filter(insp => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      insp.inspection_code.toLowerCase().includes(q) ||
      (insp.product_name_ai && insp.product_name_ai.toLowerCase().includes(q)) ||
      (insp.manufacturer_name && insp.manufacturer_name.toLowerCase().includes(q)) ||
      insp.id.toLowerCase().includes(q)
    );
  });

  useEffect(() => {
    // Fetch global counts for metrics
    const fetchMetrics = async () => {
      try {
        const [compRes, nonCompRes, inconcRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE' })
        ]);
        setCompliantCount(compRes.pagination.total_items);
        setNonCompliantCount(nonCompRes.pagination.total_items);
        setInconclusiveCount(inconcRes.pagination.total_items);
      } catch (err) {
        console.error('Failed to load metrics:', err);
      }
    };
    fetchMetrics();
  }, []);

  const compPct = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const nonCompPct = totalInspections > 0 ? ((nonCompliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const inconcPct = totalInspections > 0 ? ((inconclusiveCount / totalInspections) * 100).toFixed(1) : '0.0';
  return (
    <div className="flex-1 space-y-6 pb-8">
      {/* BREADCRUMB & HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-1">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Officer Inspection History &amp; Archive</h1>
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200/80">{totalInspections} Records • Active Cycle</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 max-w-3xl">Chronological operational log of evaluated packaged commodities, optical OCR findings, and statutory determinations under PCR 2011.</p>
        </div>
        <div className="flex items-center gap-2.5 self-start md:self-auto flex-shrink-0">
          <button 
            onClick={() => fetchPage(currentPage, statusFilter)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium shadow-sm transition-colors cursor-pointer" 
            type="button"
          >
            <Icon name="refresh" className="text-base text-slate-500" />
            <span>Refresh Stream</span>
          </button>
          <button 
            onClick={exportHistoryCSV}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium shadow-sm transition-colors cursor-pointer" 
            type="button"
          >
            <Icon name="download" className="text-base text-slate-500" />
            <span>Export History (CSV)</span>
          </button>
          <Link className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium shadow-sm transition-colors cursor-pointer" to="/app/inspection/new">
            <Icon name="add" className="text-base" />
            <span>New Inspection</span>
          </Link>
        </div>
      </div>

      {/* METRICS KPI GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between transition-all hover:border-slate-300">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Evaluated</span>
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
              <Icon name="inventory_2" className="text-lg" />
            </div>
          </div>
          <div>
            <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{totalInspections}</span>
            <div className="flex items-center gap-2 mt-2 text-xs text-slate-500 flex-wrap">
              <span className="font-medium text-slate-700">+18 today</span>
              <span>•</span>
              <span>24h active cycle</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between transition-all hover:border-emerald-300">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Compliant Records</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <Icon name="verified" className="text-lg" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{compliantCount}</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-semibold">{compPct}% Verified</span>
            </div>
            <p className="text-xs text-emerald-700 font-medium mt-2">{compPct}% compliance rate</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between transition-all hover:border-rose-300">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Non-Compliant Flagged</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <Icon name="error" className="text-lg" />
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

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between transition-all hover:border-amber-300">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Review Required</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
              <Icon name="visibility" className="text-lg" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{inconclusiveCount}</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[11px] font-semibold">{inconcPct}% Inconclusive</span>
            </div>
            <p className="text-xs text-amber-700 font-medium mt-2">Awaiting officer adjudication</p>
          </div>
        </div>
      </div>

      {/* SEARCH AND FILTER BAR */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Icon name="search" className="text-lg" />
            </div>
            <input 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm border border-slate-300 rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900" 
              placeholder="Search by Docket ID, Commodity Name, Manufacturer, or GTIN..." 
              type="text" 
            />
          </div>
          <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-2.5">
            <select 
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
              className="text-xs sm:text-sm border border-slate-300 rounded-lg bg-white px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900 font-medium"
            >
              <option value="ALL">Status: All Determinations</option>
              <option value="COMPLIANT">Compliant</option>
              <option value="NON_COMPLIANT">Non-Compliant</option>
              <option value="INCONCLUSIVE">Review Required</option>
            </select>
            <button 
              onClick={() => { setSearchQuery(''); setStatusFilter('ALL'); setCurrentPage(1); }}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors flex items-center gap-1.5 justify-center cursor-pointer" 
              title="Reset all applied filters" 
              type="button"
            >
              <Icon name="restart_alt" className="text-sm" />
              <span>Reset Filters</span>
            </button>
          </div>
        </div>
      </div>

      {/* TABLE CONTAINER */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto hidden sm:block">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 uppercase font-semibold text-[11px] tracking-wider">
              <tr>
                <th className="py-3 px-4 w-44">Docket &amp; Batch ID</th>
                <th className="py-3 px-4 min-w-[200px]">Commodity &amp; Spec</th>
                <th className="py-3 px-4 min-w-[190px]">Manufacturer / Packer</th>
                <th className="py-3 px-4 w-40">Timestamp &amp; Inspector</th>
                <th className="py-3 px-4 w-36">Statutory Status</th>
                <th className="py-3 px-4 min-w-[240px]">Primary Statutory Finding / Deficit</th>
                <th className="py-3 px-4 w-28 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-normal">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">Loading...</td>
                </tr>
              ) : filteredInspections.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">No records found.</td>
                </tr>
              ) : (
                filteredInspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 align-top">
                      <div className="font-bold text-slate-900">{insp.inspection_code}</div>
                      <div className="text-[11px] text-slate-500 font-mono mt-0.5">ID: {insp.id.substring(0, 8)}...</div>
                    </td>
                    <td className="py-3.5 px-4 align-top">
                      <div className="font-semibold text-slate-900 leading-snug">{insp.product_name_ai || 'Unknown Product'}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">Category: {insp.product_category_ai || 'N/A'}</div>
                    </td>
                    <td className="py-3.5 px-4 align-top">
                      <div className="font-medium text-slate-900">{insp.manufacturer_name || 'Unknown Manufacturer'}</div>
                    </td>
                    <td className="py-3.5 px-4 align-top">
                      <div className="font-medium text-slate-800">
                        {insp.inspection_date ? new Date(insp.inspection_date).toLocaleString() : 'N/A'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 align-top">
                      {insp.compliance_status === 'COMPLIANT' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                          COMPLIANT
                        </span>
                      )}
                      {insp.compliance_status === 'NON_COMPLIANT' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/80">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                          NON-COMPLIANT
                        </span>
                      )}
                      {(insp.compliance_status === 'INCONCLUSIVE' || insp.compliance_status === null) && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/80">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
                          {insp.compliance_status || 'PENDING'}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 align-top">
                      <div className={`font-medium leading-relaxed ${insp.compliance_status === 'COMPLIANT' ? 'text-emerald-700' : 'text-rose-700'}`}>
                        {insp.compliance_status === 'COMPLIANT' ? 'All Declarations Conforming' : 
                         insp.compliance_status === 'NON_COMPLIANT' ? `${insp.violation_count} Violations Found` :
                         'Awaiting Review'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 align-top text-right">
                      <Link className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-slate-900 hover:underline" to={`/app/inspection/${insp.id}`}>
                        <span>View Dossier</span>
                        <span aria-hidden="true">→</span>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Mobile Card-based Reflow */}
        <div className="sm:hidden divide-y divide-slate-200 border-t border-slate-200 p-2 space-y-3">
          {filteredInspections.map((insp) => (
            <div key={insp.id} className="bg-white p-3.5 rounded-lg border border-slate-200 space-y-2.5">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-bold text-slate-900 text-sm">{insp.inspection_code}</span>
                </div>
                {insp.compliance_status === 'COMPLIANT' && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                    COMPLIANT
                  </span>
                )}
                {insp.compliance_status === 'NON_COMPLIANT' && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                    NON-COMPLIANT
                  </span>
                )}
              </div>
              <div>
                <h4 className="font-medium text-xs text-slate-900">{insp.product_name_ai || 'Unknown Product'}</h4>
                <p className="text-[11px] text-slate-500">{insp.manufacturer_name}</p>
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span>{insp.inspection_date ? new Date(insp.inspection_date).toLocaleString() : 'N/A'}</span>
                <Link className="text-xs font-semibold text-slate-900 hover:underline" to={`/app/inspection/${insp.id}`}>View Dossier →</Link>
              </div>
            </div>
          ))}
        </div>

        {/* PAGINATION FOOTER */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
          <div className="text-slate-500 text-center sm:text-left">
            Showing page <strong className="font-semibold text-slate-800">{currentPage}</strong> of <strong className="font-semibold text-slate-800">{totalPages}</strong> ({totalInspections} total records)
          </div>
          <div className="flex items-center gap-1.5">
            <button 
              className="px-2.5 py-1.5 rounded-md border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 font-medium text-xs disabled:opacity-50" 
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <span className="px-3">{currentPage} / {totalPages}</span>
            <button 
              className="px-2.5 py-1.5 rounded-md border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 font-medium text-xs disabled:opacity-50" 
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OfficerHistory;
