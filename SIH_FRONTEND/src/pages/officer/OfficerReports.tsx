import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { InspectionListItem } from '../../api/types';

const OfficerReports: React.FC = () => {
  const [reports, setReports] = useState<InspectionListItem[]>([]);
  const [totalInspections, setTotalInspections] = useState<number>(0);
  const [compliantCount, setCompliantCount] = useState<number>(0);
  const [nonCompliantCount, setNonCompliantCount] = useState<number>(0);
  const [inconclusiveCount, setInconclusiveCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetricsAndReports = async () => {
      try {
        setIsLoading(true);
        const [allRes, compRes, nonCompRes, inconcRes, reportsRes] = await Promise.all([
          inspectionsApi.getInspections({ page: 1, page_size: 1 }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'NON_COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'INCONCLUSIVE' }),
          inspectionsApi.getInspections({ page: 1, page_size: 10 })
        ]);
        setTotalInspections(allRes.pagination.total_items);
        setCompliantCount(compRes.pagination.total_items);
        setNonCompliantCount(nonCompRes.pagination.total_items);
        setInconclusiveCount(inconcRes.pagination.total_items);
        setReports(reportsRes.items || []);
      } catch (err) {
        console.error('Failed to load reports data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMetricsAndReports();
  }, []);

  const compPct = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const nonCompPct = totalInspections > 0 ? ((nonCompliantCount / totalInspections) * 100).toFixed(1) : '0.0';
  const inconcPct = totalInspections > 0 ? ((inconclusiveCount / totalInspections) * 100).toFixed(1) : '0.0';

  const downloadSummaryCSV = () => {
    const headers = ['Report Ref', 'Product', 'Manufacturer', 'Date', 'Determination', 'Violations'];
    const rows = reports.map(r => [
      r.inspection_code,
      `"${r.product_name_ai || ''}"`,
      `"${r.manufacturer_name || ''}"`,
      r.inspection_date || '',
      r.compliance_status || '',
      r.violation_count || 0
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `officer_reports_summary_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex-1 space-y-6">
      {/* Breadcrumb & Top Bar */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-500 font-mono">
          <span className="hover:text-slate-800 cursor-pointer">Officer Portal</span>
          <span className="text-slate-300">/</span>
          <span className="hover:text-slate-800 cursor-pointer">Archives</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-800 font-semibold">Generated Officer Reports</span>
        </div>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Officer Reports &amp; Export Repository</h1>
              <span className="px-2.5 py-0.5 bg-slate-200/70 text-slate-700 text-xs font-semibold rounded-full">{totalInspections} Dossiers</span>
            </div>
            <p className="text-sm text-slate-500 mt-1">Review verified inspection reports, statutory deficit notices, and standard export pipelines.</p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
            <button 
              onClick={downloadSummaryCSV}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors cursor-pointer" 
              type="button"
            >
              <Icon name="summarize" className="text-[16px]" />
              <span>Generate Summary Report</span>
            </button>
            <button 
              onClick={downloadSummaryCSV}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-sm transition-colors cursor-pointer" 
              type="button"
            >
              <Icon name="archive" className="text-[16px]" />
              <span>Batch Export (CSV)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Regulatory Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase tracking-wider font-semibold">Statutory Deficits</span>
            <Icon name="gavel" className="text-[20px] text-rose-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{nonCompliantCount}</span>
            <span className="text-xs text-rose-600 font-medium">{nonCompPct}% Non-Compliant</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-rose-500 h-full rounded-full" style={{ width: `${nonCompPct}%` }}></div>
          </div>
          <span className="block text-[11px] text-slate-400 truncate">Font height &amp; mandatory USP deficits</span>
        </div>
        <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase tracking-wider font-semibold">Fully Compliant</span>
            <Icon name="verified" className="text-[20px] text-emerald-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{compliantCount}</span>
            <span className="text-xs text-emerald-700 font-medium">{compPct}% Cleared</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${compPct}%` }}></div>
          </div>
          <span className="block text-[11px] text-slate-400 truncate">All statutory declarations verified</span>
        </div>
        <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase tracking-wider font-semibold">Review Required</span>
            <Icon name="pending_actions" className="text-[20px] text-amber-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{inconclusiveCount}</span>
            <span className="text-xs text-amber-700 font-medium">Under Adjudication</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-amber-500 h-full rounded-full" style={{ width: `${inconcPct}%` }}></div>
          </div>
          <span className="block text-[11px] text-slate-400 truncate">OCR ambiguity &amp; contrast check</span>
        </div>
        <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase tracking-wider font-semibold">Total Dossiers</span>
            <Icon name="folder_open" className="text-[20px] text-slate-700" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{totalInspections}</span>
            <span className="text-xs text-slate-500 font-medium">All Cycles</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-slate-900 h-full rounded-full" style={{ width: '100%' }}></div>
          </div>
          <span className="block text-[11px] text-slate-400 truncate">Central statutory repository synced</span>
        </div>
      </div>

      {/* Search, Filter & Multi-criteria Bar */}
      <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
          {/* Search input */}
          <div className="relative flex-1 min-w-[240px]">
            <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-slate-400" />
            <input className="w-full pl-9 pr-8 py-2 bg-slate-50 text-slate-900 placeholder:text-slate-400 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-1 focus:ring-slate-900 focus:bg-white transition-all" placeholder="Search by Docket or Commodity..." type="text" />
          </div>
          {/* Filters group */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-2">
            {/* Date range dropdown */}
            <div className="relative">
              <select className="appearance-none bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs pl-3 pr-8 py-2 rounded-lg border border-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer" defaultValue="thismonth">
                <option value="all">Date: All Periods</option>
                <option value="today">Today</option>
                <option value="last7">Last 7 Days</option>
                <option value="thismonth">March 2026 (Q1)</option>
              </select>
              <Icon name="expand_more" className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[16px] text-slate-400" />
            </div>
            {/* Determination filter */}
            <div className="relative">
              <select className="appearance-none bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs pl-3 pr-8 py-2 rounded-lg border border-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer" defaultValue="all">
                <option value="all">Determination: All</option>
                <option value="compliant">Compliant</option>
                <option value="deficit">Non-Compliant</option>
                <option value="pending">Review Required</option>
              </select>
              <Icon name="expand_more" className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[16px] text-slate-400" />
            </div>
            {/* Format selector */}
            <div className="relative">
              <select className="appearance-none bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs pl-3 pr-8 py-2 rounded-lg border border-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer" defaultValue="all">
                <option value="all">Format: All Formats</option>
                <option value="pdf">PDF Dossier</option>
                <option value="csv">CSV Metadata</option>
                <option value="bundle">Evidence Bundle</option>
              </select>
              <Icon name="expand_more" className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[16px] text-slate-400" />
            </div>
            {/* Refresh button */}
            <button className="p-2 bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 rounded-lg transition-colors" title="Reload Repository">
              <Icon name="refresh" className="text-[18px]" />
            </button>
          </div>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 font-mono">
          <div className="flex items-center gap-2">
            <span>Showing:</span>
            <span className="font-semibold text-slate-800">{reports.length} of {totalInspections} Records</span>
            <span className="text-slate-300">·</span>
            <span>All Cycles</span>
          </div>
          <div className="flex items-center gap-3">
            <button className="hover:text-slate-900 underline">Select Visible</button>
            <span className="text-slate-300">/</span>
            <button className="hover:text-slate-900 underline">Deselect All</button>
          </div>
        </div>
      </div>

      {/* Reports Table (Desktop & Tablet) */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[900px]">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
                <th className="py-3 px-4 w-10">
                  <input className="rounded w-3.5 h-3.5 text-slate-900 focus:ring-0 cursor-pointer border-slate-300" type="checkbox" />
                </th>
                <th className="py-3 px-3">Report Reference</th>
                <th className="py-3 px-3">Commodity &amp; Docket</th>
                <th className="py-3 px-3">Manufacturer / Packer</th>
                <th className="py-3 px-3">Date Generated</th>
                <th className="py-3 px-3">Statutory Determination</th>
                <th className="py-3 px-3">Primary Statutory Finding</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">Loading reports...</td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">No reports found</td>
                </tr>
              ) : reports.map((report) => {
                const isNonCompliant = report.compliance_status === 'NON_COMPLIANT';
                const isCompliant = report.compliance_status === 'COMPLIANT';
                return (
                  <tr key={report.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 align-top">
                      <input className="rounded w-3.5 h-3.5 text-slate-900 focus:ring-0 cursor-pointer border-slate-300" type="checkbox" />
                    </td>
                    <td className="py-3.5 px-3 align-top font-mono">
                      <span className="font-semibold text-slate-900 block">{report.inspection_code}</span>
                      <span className="text-[11px] text-slate-400">Dossier</span>
                    </td>
                    <td className="py-3.5 px-3 align-top">
                      <span className="font-semibold text-slate-900 block truncate max-w-[200px]">{report.product_name_ai || 'Unknown Product'}</span>
                      <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono">
                        <Icon name="inventory_2" className="text-[13px]" />
                        <span>{report.product_category_ai || 'Uncategorized'}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3 align-top">
                      <span className="font-medium text-slate-900 block truncate max-w-[190px]">{report.manufacturer_name || 'Unknown Manufacturer'}</span>
                    </td>
                    <td className="py-3.5 px-3 align-top whitespace-nowrap font-mono">
                      <span className="text-slate-900 font-medium block">{report.inspection_date ? new Date(report.inspection_date).toLocaleDateString() : 'N/A'}</span>
                    </td>
                    <td className="py-3.5 px-3 align-top whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-semibold text-[11px] border ${
                        isNonCompliant ? 'bg-rose-50 text-rose-700 border-rose-200/50' : 
                        (isCompliant ? 'bg-emerald-50 text-emerald-700 border-emerald-200/50' : 'bg-amber-50 text-amber-800 border-amber-200/50')
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${
                          isNonCompliant ? 'bg-rose-600' : (isCompliant ? 'bg-emerald-600' : 'bg-amber-600')
                        }`}></span>
                        {report.compliance_status || 'PENDING'}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 align-top max-w-[240px]">
                      <div className="space-y-0.5">
                        {isNonCompliant ? (
                          <>
                            <div className="flex items-center gap-1 font-semibold text-rose-700 text-[11px]">
                              <Icon name="error" className="text-[14px]" />
                              <span>{report.violation_count} Violations detected</span>
                            </div>
                            <p className="text-[11px] text-slate-500 leading-snug">Requires statutory rectification.</p>
                          </>
                        ) : isCompliant ? (
                          <>
                            <div className="flex items-center gap-1 font-semibold text-emerald-700 text-[11px]">
                              <Icon name="check_circle" className="text-[14px]" />
                              <span>Declarations Compliant</span>
                            </div>
                            <p className="text-[11px] text-slate-500 leading-snug">All statutory requirements met.</p>
                          </>
                        ) : (
                          <>
                            <div className="flex items-center gap-1 font-semibold text-amber-800 text-[11px]">
                              <Icon name="help_center" className="text-[14px]" />
                              <span>Review Required</span>
                            </div>
                            <p className="text-[11px] text-slate-500 leading-snug">Officer verification needed.</p>
                          </>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 align-top text-right whitespace-nowrap">
                      <Link to={`/app/inspection/${report.id}`} className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-semibold text-xs transition-colors">
                        <span>View</span>
                        <Icon name="arrow_forward" className="text-[14px]" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {/* Table Pagination Footer */}
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <span className="text-slate-500 font-mono">Showing {reports.length} of {totalInspections} records · Sorted by Generation Timestamp (Desc)</span>
          <div className="flex items-center gap-1">
            <button className="px-2.5 py-1 bg-white text-slate-400 border border-slate-200 rounded font-medium disabled:opacity-50 cursor-not-allowed" disabled>Previous</button>
            <span className="px-2.5 py-1 bg-slate-900 text-white rounded font-semibold">1</span>
            <button className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded font-medium transition-colors">2</button>
            <button className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded font-medium transition-colors">3</button>
            <button className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded font-medium transition-colors">Next</button>
          </div>
        </div>
      </div>

      {/* Export Schemas & Templates section */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">Export Schemas &amp; Templates</h2>
            <p className="text-xs text-slate-500">Standard export formats for officer inspection records and analysis pipelines.</p>
          </div>
          <span className="text-xs font-mono text-slate-600 bg-slate-200/70 px-2.5 py-1 rounded-md font-semibold">PCR-2011 Formats</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1 */}
          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-slate-900 text-white text-[10px] font-mono uppercase font-bold">PDF DOSSIER</span>
                <span className="text-xs font-mono text-slate-400">Standard v2.4</span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">Inspection Summary Dossier</h3>
              <p className="text-xs text-slate-500 leading-relaxed">Official document including inspection docket ID, OCR verification tables, detected font-height ratios, and rule infractions.</p>
            </div>
            <div className="space-y-2 pt-2">
              <div className="p-2.5 bg-slate-50 rounded-lg space-y-1 text-xs text-slate-500 font-mono">
                <div className="flex justify-between"><span>Format:</span><span className="text-slate-900 font-medium">A4 PDF Document</span></div>
                <div className="flex justify-between"><span>Level:</span><span className="text-slate-900 font-medium">Official Officer Record</span></div>
                <div className="flex justify-between"><span>Est Size:</span><span className="text-slate-900 font-medium">4.1 MB</span></div>
              </div>
              <button className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-1.5" type="button">
                <Icon name="visibility" className="text-[15px]" />
                <span>Preview Format</span>
              </button>
            </div>
          </div>
          {/* Card 2 */}
          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-800 text-[10px] font-mono uppercase font-bold">EVIDENCE PACKAGE</span>
                <span className="text-xs font-mono text-slate-400">High-Res PNG</span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">Bounding Box &amp; OCR Evidence</h3>
              <p className="text-xs text-slate-500 leading-relaxed">Full evidentiary crop package containing original packaging captures, rectangular coordinate bounding boxes, and luminance histograms.</p>
            </div>
            <div className="space-y-2 pt-2">
              <div className="p-2.5 bg-slate-50 rounded-lg space-y-1 text-xs text-slate-500 font-mono">
                <div className="flex justify-between"><span>Resolution:</span><span className="text-slate-900 font-medium">300 DPI Optical</span></div>
                <div className="flex justify-between"><span>Attachments:</span><span className="text-slate-900 font-medium">Crops &amp; Annotations</span></div>
                <div className="flex justify-between"><span>Format:</span><span className="text-slate-900 font-medium">PNG + JSON Coordinates</span></div>
              </div>
              <button className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-1.5" type="button">
                <Icon name="visibility" className="text-[15px]" />
                <span>Preview Evidence Schema</span>
              </button>
            </div>
          </div>
          {/* Card 3 */}
          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-white text-[10px] font-mono uppercase font-bold">METADATA CSV</span>
                <span className="text-xs font-mono text-slate-400">UTF-8 / Excel</span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">Inspection Metadata &amp; Deficit Log</h3>
              <p className="text-xs text-slate-500 leading-relaxed">Tabular export structured for department analytics pipelines, manufacturer compliance tracking, and recurring deficit analysis.</p>
            </div>
            <div className="space-y-2 pt-2">
              <div className="p-2.5 bg-slate-50 rounded-lg space-y-1 text-xs text-slate-500 font-mono">
                <div className="flex justify-between"><span>Columns:</span><span className="text-slate-900 font-medium">24 Regulatory Fields</span></div>
                <div className="flex justify-between"><span>Compatibility:</span><span className="text-slate-900 font-medium">Excel, ERP, CSV</span></div>
                <div className="flex justify-between"><span>Encoding:</span><span className="text-slate-900 font-medium">UTF-8 Standard</span></div>
              </div>
              <button className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-1.5" type="button">
                <Icon name="visibility" className="text-[15px]" />
                <span>View Data Dictionary</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OfficerReports;
