import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionListItem } from '../../api/types';

const ScanHistory: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'all' | 'COMPLIANT' | 'NON_COMPLIANT' | 'INCONCLUSIVE'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dateFilter, setDateFilter] = useState('30');
  
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [totalInspections, setTotalInspections] = useState<number>(0);
  const [compliantCount, setCompliantCount] = useState<number>(0);
  const [nonCompliantCount, setNonCompliantCount] = useState<number>(0);
  const [inconclusiveCount, setInconclusiveCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPage = async (page: number, status?: string) => {
    try {
      setIsLoading(true);
      const params: any = { page, page_size: 10, scope: 'user' };
      if (status && status !== 'all') {
        params.compliance_status = status;
      }
      if (searchQuery) {
        params.q = searchQuery;
      }
      if (dateFilter && dateFilter !== 'all') {
        const date = new Date();
        date.setDate(date.getDate() - parseInt(dateFilter, 10));
        params.start_date = date.toISOString();
      }
      const res = await inspectionsApi.getInspections(params);
      setInspections(res.items);
      setTotalPages(res.pagination.total_pages);
      // We only set total counts on init, but we can set the filtered length here if needed.
    } catch (err) {
      console.error('Failed to load scan history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Basic debounce for search query
    const timer = setTimeout(() => {
      fetchPage(currentPage, activeTab);
    }, 300);
    return () => clearTimeout(timer);
  }, [currentPage, activeTab, searchQuery, dateFilter]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [allRes, compRes, nonCompRes, inconcRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1, scope: 'user' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT', scope: 'user' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT', scope: 'user' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE', scope: 'user' })
        ]);
        setTotalInspections(allRes.pagination.total_items);
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
  const exportUserCSV = () => {
    const headers = ['Scan ID', 'Product', 'Manufacturer', 'Timestamp', 'Status', 'Violations'];
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
    link.setAttribute('download', `user_scan_history_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col w-full pb-10">
      {/* Top Breadcrumb & Metadata Strip */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-3 pb-2 border-b border-slate-200/50 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-slate-900 tracking-tight">Scan History &amp; Archive</span>
        </div>
        <div className="flex items-center gap-2 text-slate-500 font-mono text-[10px] font-medium">
          <Icon name="history" className="text-[14px]" />
          <span>Updated just now</span>
        </div>
      </div>

      {/* Screen Header: Title + Strategic Actions */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
        <div className="flex flex-col gap-2 max-w-3xl">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Scan History &amp; Archive</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-bold text-[10px] tracking-wide uppercase">{totalInspections} Records</span>
          </div>
          <p className="text-sm text-slate-500 leading-relaxed">Records of packaging compliance scans, verification summaries, and inspection reports.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button 
            onClick={exportUserCSV}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm text-sm font-bold focus:outline-none cursor-pointer" 
            type="button"
          >
            <Icon name="download" className="text-[18px] text-slate-500" />
            <span>Export History (CSV)</span>
          </button>
          <button 
            className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors focus:outline-none w-full sm:w-auto mt-2 sm:mt-0" 
            onClick={() => navigate('/app/user/scan/new')}
            type="button"
          >
            <Icon name="add" className="text-[18px]" />
            <span>New Scan</span>
          </button>
        </div>
      </div>

      {/* Analytical Summary Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Total Evaluated</span>
            <Icon name="inventory_2" className="text-[18px] text-slate-400" />
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-slate-900">{totalInspections}</span>
            <span className="font-mono text-[10px] text-slate-500 font-medium">100% Volume</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-slate-800 h-full w-full"></div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-emerald-700 uppercase tracking-wider font-bold">Compliant Units</span>
            <Icon name="check_circle" className="text-[18px] text-emerald-600" />
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-emerald-700">{compliantCount}</span>
            <span className="font-mono text-[10px] text-emerald-600 font-bold">{compPct}% Clearance</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-emerald-500 h-full" style={{ width: `${compPct}%` }}></div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-rose-700 uppercase tracking-wider font-bold">Non-Compliant</span>
            <Icon name="error" className="text-[18px] text-rose-600" />
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-rose-600">{nonCompliantCount}</span>
            <span className="font-mono text-[10px] text-rose-600 font-bold">{nonCompPct}% Flag Rate</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-rose-600 h-full" style={{ width: `${nonCompPct}%` }}></div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-amber-700 uppercase tracking-wider font-bold">Manual Review Required</span>
            <Icon name="pending_actions" className="text-[18px] text-amber-600" />
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-amber-600">{inconclusiveCount}</span>
            <span className="font-mono text-[10px] text-amber-600 font-bold">Adjudication Pending</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-amber-500 h-full" style={{ width: `${inconcPct}%` }}></div>
          </div>
        </div>
      </div>

      {/* Filter, Search & Parametric Controls Module */}
      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 p-4 mb-6 flex flex-col gap-4">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
          {/* Search Input Container */}
          <div className="relative flex-1">
            <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-slate-400" />
            <input 
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-900 placeholder:text-slate-400 text-sm focus:outline-none focus:bg-white focus:ring-1 focus:ring-slate-900 transition-all" 
              placeholder="Search by product name, barcode, or scan ID..." 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          {/* Quick Date Filter & Auxiliary Dropdowns */}
          <div className="flex items-center gap-3">
            <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5">
              <Icon name="calendar_today" className="text-[16px] text-slate-500 mr-2" />
              <select 
                className="bg-transparent text-slate-900 text-xs font-bold focus:outline-none cursor-pointer pr-4 appearance-none outline-none"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              >
                <option value="30">Last 30 Days</option>
                <option value="7">Last 7 Days</option>
                <option value="90">Current Quarter (90 Days)</option>
                <option value="all">Full Historical Archive</option>
              </select>
            </div>
            <button className="flex items-center justify-center p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100 transition-colors focus:outline-none" title="Refine Filters" type="button">
              <Icon name="filter_list" className="text-[18px]" />
            </button>
          </div>
        </div>

        {/* Segmented Status Tabs */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
          <button 
            className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 transition-colors focus:outline-none ${activeTab === 'all' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}`} 
            onClick={() => { setActiveTab('all'); setCurrentPage(1); }}
            type="button"
          >
            <span>All Scans</span>
            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${activeTab === 'all' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500'}`}>{totalInspections}</span>
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 transition-colors focus:outline-none ${activeTab === 'COMPLIANT' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-sm' : 'text-slate-600 hover:bg-slate-100 border border-transparent'}`} 
            onClick={() => { setActiveTab('COMPLIANT'); setCurrentPage(1); }}
            type="button"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
            <span>Compliant</span>
            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${activeTab === 'COMPLIANT' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'}`}>{compliantCount}</span>
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 transition-colors focus:outline-none ${activeTab === 'NON_COMPLIANT' ? 'bg-rose-50 text-rose-700 border border-rose-200 shadow-sm' : 'text-slate-600 hover:bg-slate-100 border border-transparent'}`} 
            onClick={() => { setActiveTab('NON_COMPLIANT'); setCurrentPage(1); }}
            type="button"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500"></span>
            <span>Non-Compliant</span>
            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${activeTab === 'NON_COMPLIANT' ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-500'}`}>{nonCompliantCount}</span>
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center gap-2 transition-colors focus:outline-none ${activeTab === 'INCONCLUSIVE' ? 'bg-amber-50 text-amber-700 border border-amber-200 shadow-sm' : 'text-slate-600 hover:bg-slate-100 border border-transparent'}`} 
            onClick={() => { setActiveTab('INCONCLUSIVE'); setCurrentPage(1); }}
            type="button"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
            <span>Manual Review Required</span>
            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${activeTab === 'INCONCLUSIVE' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-500'}`}>{inconclusiveCount}</span>
          </button>
        </div>
      </div>

      {/* Primary Desktop & Tablet Tabular Archive View */}
      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 overflow-hidden mb-6 hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Scan ID</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Product &amp; Commodity</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Scan Timestamp</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Compliance Status</th>
                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Primary Flag / Verification Summary</th>

                <th className="py-3 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500 font-medium">Loading scans...</td>
                </tr>
              ) : inspections.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500 font-medium">No scans found.</td>
                </tr>
              ) : inspections.map((scan) => {
                const isNonCompliant = scan.compliance_status === 'NON_COMPLIANT';
                const isReview = scan.compliance_status === 'INCONCLUSIVE' || scan.compliance_status === null;
                const dateObj = scan.inspection_date ? new Date(scan.inspection_date) : null;
                
                return (
                  <tr key={scan.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="py-4 px-4 align-top">
                      <span className="font-mono text-[10px] text-slate-700 px-2 py-1 rounded bg-slate-100 border border-slate-200 font-bold block w-fit shadow-sm">{scan.inspection_code}</span>
                    </td>
                    <td className="py-4 px-4 align-top max-w-xs">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900 leading-snug">{scan.product_name_ai || 'Unknown Product'}</span>
                        <span className="text-xs text-slate-500 mt-0.5">{scan.manufacturer_name}</span>
                        <span className="font-mono text-[10px] text-slate-400 mt-1 font-medium">Category: {scan.product_category_ai || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 align-top whitespace-nowrap">
                      <span className="text-sm font-bold text-slate-900 block">{dateObj ? dateObj.toLocaleDateString() : 'N/A'}</span>
                      <span className="font-mono text-[10px] text-slate-500 font-medium">{dateObj ? dateObj.toLocaleTimeString() : ''}</span>
                    </td>
                    <td className="py-4 px-4 align-top whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded border text-[10px] font-bold tracking-wide uppercase ${
                        isNonCompliant ? 'bg-rose-50 text-rose-700 border-rose-200' :
                        isReview ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}>
                        {isNonCompliant ? (
                          <span className="h-1.5 w-1.5 rounded-full bg-rose-600"></span>
                        ) : isReview ? (
                          <Icon name="warning" className="text-[13px]" />
                        ) : (
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-600"></span>
                        )}
                        {scan.compliance_status || 'PENDING'}
                      </span>
                    </td>
                    <td className="py-4 px-4 align-top">
                      <div className="flex flex-col gap-1.5">
                        <span className={`text-xs font-bold flex items-start gap-1.5 leading-snug ${
                          isNonCompliant ? 'text-rose-600' :
                          isReview ? 'text-amber-700' :
                          'text-emerald-700'
                        }`}>
                          <Icon name={isNonCompliant ? 'straighten' : isReview ? 'wb_incandescent' : 'check'} className="text-[16px] mt-0.5 shrink-0" />
                          {isNonCompliant ? `${scan.violation_count} Violations` : isReview ? 'Awaiting Review' : 'All Declarations Conforming'}
                        </span>
                      </div>
                    </td>

                    <td className="py-4 px-4 align-top text-right whitespace-nowrap">
                      <button 
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 hover:bg-slate-100 transition-colors text-xs font-bold focus:outline-none group"
                        onClick={() => navigate(`/app/user/reports/${scan.id}`)}
                        type="button"
                      >
                        <span>View Report</span>
                        <Icon name="arrow_forward" className="text-[15px] group-hover:translate-x-0.5 transition-transform" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between gap-4">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-slate-600 font-medium">Page {currentPage} of {totalPages}</span>
          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}

    </div>
  );
};

export default ScanHistory;
