import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { analyticsApi } from '../../api/analytics';
import { manufacturersApi } from '../../api/manufacturers';
import type { ManufacturerAnalytics, ManufacturerHistoryItem } from '../../api/types';

const ManufacturerRepeat: React.FC = () => {
  const [offenders, setOffenders] = useState<ManufacturerAnalytics[]>([]);
  const [activeOffender, setActiveOffender] = useState<ManufacturerAnalytics | null>(null);
  const [history, setHistory] = useState<ManufacturerHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOffenders = async () => {
      try {
        setIsLoading(true);
        const res = await analyticsApi.getRepeatOffenders();
        setOffenders(res.offenders || []);
        if (res.offenders && res.offenders.length > 0) {
          setActiveOffender(res.offenders[0]);
        }
      } catch (err) {
        console.error('Failed to load repeat offenders:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchOffenders();
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!activeOffender) return;
      try {
        const res = await manufacturersApi.getManufacturerHistory(activeOffender.manufacturer_id, { page: 1, page_size: 10 });
        setHistory(res.items || []);
      } catch (err) {
        console.error('Failed to load manufacturer history:', err);
      }
    };
    fetchHistory();
  }, [activeOffender]);
  return (
    <div className="flex flex-col w-full space-y-6 pb-8">
{/*  Sub-Header & Breadcrumb Bar  */}
<div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md pt-space-xs">
<div className="flex flex-col space-y-space-2xs min-w-0"><div className="flex items-center gap-space-xs font-code-sm text-code-sm text-on-surface-variant"><span className="hover:text-on-surface cursor-pointer">Officer Portal</span><span className="text-outline-variant">/</span><span className="text-on-surface font-semibold">Manufacturer Compliance Profiles</span></div><h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight truncate">Manufacturer Compliance Profiles &amp; Recurring Findings</h1><p className="font-body-sm text-body-sm text-on-surface-variant">Objective verification logs, recurring statutory deficits, and audited packaging histories under PCR 2011 / LM Act.</p></div>
{/*  Search & Scope Controls  */}
<div className="flex items-center gap-space-sm w-full md:w-auto">
<div className="relative flex-1 md:w-80">
<Icon name="search" className="absolute left-space-sm top-1/2 -translate-y-1/2 text-[18px] text-on-surface-variant" />
<input className="w-full pl-9 pr-space-base py-space-xs h-9 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-outline" id="manufacturer-search-input" placeholder="Search manufacturer or brand name (e.g., Pristine Valleys)..." type="text" value={activeOffender?.manufacturer_name || ''} readOnly />
</div>
<button className="h-9 px-space-md bg-surface-container-lowest hover:bg-surface-container-high text-on-surface text-label-md font-label-md rounded flex items-center gap-space-xs shadow-sm transition-colors">
<Icon name="filter_list" className="text-[18px]" />
<span className="">Filter</span>
</button>
</div>
</div>
{/*  Main Asymmetric Workspace Layout  */}
<div className="grid grid-cols-1 xl:grid-cols-12 gap-space-lg items-start">
{/*  Primary Content Column: Active Entity & Technical Findings (8 of 12 Cols)  */}
<div className="xl:col-span-8 flex flex-col space-y-space-lg min-w-0">
{/*  Active Manufacturer Summary Profile Card  */}
<div className="bg-surface-container-lowest rounded shadow-sm overflow-hidden flex flex-col">
{/*  Card Header with Regulatory Standard Indicators  */}
<div className="p-space-base bg-surface-container-low flex flex-wrap items-center justify-between gap-space-sm"><div className="flex items-center gap-space-sm"><span className="w-2.5 h-2.5 rounded-full bg-secondary"></span><span className="font-label-sm text-label-sm text-on-secondary-container uppercase tracking-wider">Entity Profile #{activeOffender ? activeOffender.manufacturer_id.slice(0, 8) : '---'}</span></div><div className="flex items-center gap-space-xs font-code-sm text-code-sm text-on-surface-variant bg-surface-container px-space-sm py-space-2xs rounded"><Icon name="verified" className="text-[14px]" /><span className="">Verified Entity Record</span></div></div>
<div className="p-space-lg flex flex-col space-y-space-lg">
{/*  Entity Identity Row  */}
<div className="flex flex-col md:flex-row justify-between md:items-start gap-space-md">
<div className="space-y-space-2xs min-w-0">
<div className="flex items-center gap-space-xs flex-wrap">
<h2 className="font-headline-md text-headline-md text-on-surface font-semibold tracking-tight">
                  {activeOffender ? activeOffender.manufacturer_name : 'Loading...'}
                </h2>
<span className="px-space-xs py-space-2xs bg-surface-container font-code-sm text-code-sm text-on-surface-variant rounded">CIN: U15400PN2018PTC178921</span>
</div>
<div className="flex items-center gap-space-xs text-on-surface-variant font-body-sm text-body-sm">
<Icon name="factory" className="text-[16px] text-secondary" />
<span className="">Premises: Plot 14, MIDC Industrial Area, Pune 411028 | FSSAI Lic: 11521034000492</span>
</div>
</div>
{/*  Repeat Discrepancy Flag Callout  */}
{activeOffender && activeOffender.repeat_violation_count > 0 && (
<div className="bg-error-container/40 p-space-sm rounded flex items-start gap-space-sm shrink-0 md:max-w-xs">
<Icon name="warning" className="text-error text-[20px] mt-0.5" />
<div className="flex flex-col min-w-0">
<span className="font-label-sm text-label-sm text-on-error-container uppercase tracking-wide">Active Deficit Pattern</span>
<span className="font-headline-sm text-headline-sm text-error font-semibold leading-snug">Repeat Violations: {activeOffender.repeat_violation_count}</span>
<span className="font-code-sm text-code-sm text-on-surface-variant">Top code: {activeOffender.top_violation_codes[0] || 'Unknown'}</span>
</div>
</div>
)}
</div>
{/*  Quick Metrics Bento Row  */}
<div className="grid grid-cols-2 md:grid-cols-4 gap-space-sm"><div className="bg-surface-container-low p-space-md rounded flex flex-col justify-between space-y-space-xs"><div className="flex items-center justify-between text-on-surface-variant"><span className="font-label-sm text-label-sm uppercase tracking-wider">Total Scans</span><Icon name="inventory_2" className="text-[18px]" /></div><div><span className="font-headline-lg text-headline-lg text-on-surface font-bold">{activeOffender ? activeOffender.total_inspections : 0}</span><span className="font-body-sm text-body-sm text-on-surface-variant block">Packages Evaluated</span></div></div><div className="bg-surface-container-low p-space-md rounded flex flex-col justify-between space-y-space-xs"><div className="flex items-center justify-between text-error"><span className="font-label-sm text-label-sm uppercase tracking-wider">Deficits</span><Icon name="report_problem" className="text-[18px]" /></div><div><div className="flex items-baseline gap-space-xs"><span className="font-headline-lg text-headline-lg text-error font-bold">{activeOffender ? activeOffender.total_violations : 0}</span></div><span className="font-body-sm text-body-sm text-on-surface-variant block">Non-Compliant Findings</span></div></div><div className="col-span-2 bg-surface-container-low p-space-md rounded flex flex-col justify-between space-y-space-xs"><div className="flex items-center justify-between text-on-tertiary-container"><span className="font-label-sm text-label-sm uppercase tracking-wider">Compliance Summary</span><Icon name="info" className="text-[18px]" /></div><div><span className="font-body-sm text-body-sm text-on-surface-variant block">{activeOffender ? activeOffender.compliance_summary : 'Loading...'}</span></div></div></div>
</div>
</div>
{/*  Violation & Finding Pattern Analysis Section  */}
<div className="bg-surface-container-lowest rounded shadow-sm flex flex-col p-space-lg space-y-space-base">
<div className="flex flex-col md:flex-row justify-between md:items-center gap-space-xs">
<div>
<h3 className="font-headline-md text-headline-md text-on-surface font-semibold">
              Violation &amp; Finding Pattern Analysis
            </h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">
              Historical Discrepancies aggregated from optical OCR character segmentation and statutory dimension tests.
            </p>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant bg-surface-container-low px-space-sm py-space-2xs rounded self-start md:self-auto">
            Audit Range: Oct 2025 – Present
          </span>
</div>
{/*  Visual Progress Rings & Stat Cards  */}
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-base">
{/*  Deficit Item 1  */}
<div className="bg-surface-container-low p-space-base rounded flex flex-col justify-between space-y-space-md">
<div className="flex items-start justify-between">
<div>
<span className="font-label-sm text-label-sm text-error font-semibold uppercase">Primary Trend</span>
<h4 className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-space-2xs">
                  Numeral Height Below Mandate
                </h4>
<span className="font-code-sm text-code-sm text-on-surface-variant">Rule 6(1)(h) / Table 1 (LM Act)</span>
</div>
{/*  Inline Micro SVG Chart  */}
<svg className="w-10 h-10 text-error shrink-0" viewBox="0 0 36 36">
<path className="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3.5"></path>
<path className="text-error" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="80, 100" stroke-linecap="round" stroke-width="3.5"></path>
</svg>
</div>
<div className="space-y-space-xs">
<div className="flex items-center justify-between font-body-sm text-body-sm">
<span className="text-on-surface font-medium">4 occurrences</span>
<span className="text-on-surface-variant font-code-sm text-code-sm">Across 3 commodities</span>
</div>
<div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
<div className="bg-error h-full rounded-full w-4/5"></div>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant pt-space-xs">
                Observed heights of 1.4mm - 1.8mm against statutory requirement of ≥ 2.0mm for net weights up to 500g.
              </p>
</div>
</div>
{/*  Deficit Item 2  */}
<div className="bg-surface-container-low p-space-base rounded flex flex-col justify-between space-y-space-md">
<div className="flex items-start justify-between">
<div>
<span className="font-label-sm text-label-sm text-on-secondary-container font-semibold uppercase">Secondary Trend</span>
<h4 className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-space-2xs">
                  Consumer Care Email Missing
                </h4>
<span className="font-code-sm text-code-sm text-on-surface-variant">Rule 6(1)(da) (PCR 2011)</span>
</div>
<svg className="w-10 h-10 text-secondary shrink-0" viewBox="0 0 36 36">
<path className="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3.5"></path>
<path className="text-secondary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="40, 100" stroke-linecap="round" stroke-width="3.5"></path>
</svg>
</div>
<div className="space-y-space-xs">
<div className="flex items-center justify-between font-body-sm text-body-sm">
<span className="text-on-surface font-medium">2 occurrences</span>
<span className="text-on-surface-variant font-code-sm text-code-sm">Repeated in lot HON-A</span>
</div>
<div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
<div className="bg-secondary h-full rounded-full w-2/5"></div>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant pt-space-xs">
                Physical grievance phone number present, but mandatory digital contact point (email address) omitted.
              </p>
</div>
</div>
{/*  Deficit Item 3  */}
<div className="bg-surface-container-low p-space-base rounded flex flex-col justify-between space-y-space-md">
<div className="flex items-start justify-between">
<div>
<span className="font-label-sm text-label-sm text-outline font-semibold uppercase">Isolated Finding</span>
<h4 className="font-headline-sm text-headline-sm text-on-surface font-semibold mt-space-2xs">
                  Net Quantity Font Contrast
                </h4>
<span className="font-code-sm text-code-sm text-on-surface-variant">Rule 9(1) Legibility Clause</span>
</div>
<svg className="w-10 h-10 text-outline shrink-0" viewBox="0 0 36 36">
<path className="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3.5"></path>
<path className="text-outline" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="20, 100" stroke-linecap="round" stroke-width="3.5"></path>
</svg>
</div>
<div className="space-y-space-xs">
<div className="flex items-center justify-between font-body-sm text-body-sm">
<span className="text-on-surface font-medium">1 occurrence</span>
<span className="text-on-surface-variant font-code-sm text-code-sm">Single batch flag</span>
</div>
<div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
<div className="bg-outline h-full rounded-full w-1/5"></div>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant pt-space-xs">
                Light amber font superimposed on clear honey packaging failing standard optical contrast threshold.
              </p>
</div>
</div>
</div>
</div>
{/*  Historical Manufacturer Inspections List  */}
<div className="bg-surface-container-lowest rounded shadow-sm flex flex-col">
<div className="p-space-base bg-surface-container-low flex flex-col sm:flex-row justify-between sm:items-center gap-space-sm">
<div>
<h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">
              Inspection Dossiers Under Active Entity
            </h3>
<span className="font-body-sm text-body-sm text-on-surface-variant">
              Chronological log of commodities examined by field officers.
            </span>
</div>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-space-2xs bg-surface-container-lowest hover:bg-surface-container-high text-on-surface font-code-sm text-code-sm rounded shadow-sm flex items-center gap-space-xs">
<Icon name="file_download" className="text-[14px]" />
<span className="">Export CSV Dossier</span>
</button>
</div>
</div>
{/*  Table View with Responsive Scrolling  */}
<div className="overflow-x-auto">
<table className="w-full text-left border-collapse">
<thead>
<tr className="bg-surface-container-low/50 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider">
<th className="py-space-sm px-space-base font-semibold">Inspection ID</th>
<th className="py-space-sm px-space-base font-semibold">Commodity &amp; Packaging</th>
<th className="py-space-sm px-space-base font-semibold">Compliance Status</th>
<th className="py-space-sm px-space-base font-semibold">Primary Statutory Finding</th>
<th className="py-space-sm px-space-base font-semibold text-right">Action</th>
</tr>
</thead>
<tbody className="divide-y divide-surface-container font-body-sm text-body-sm">
{history.length === 0 ? (
  <tr>
    <td colSpan={5} className="py-space-md px-space-base text-center text-on-surface-variant">No history found.</td>
  </tr>
) : history.map((item) => {
  const isNonCompliant = item.compliance_status === 'NON_COMPLIANT';
  const dateObj = item.inspection_date ? new Date(item.inspection_date) : null;
  return (
    <tr key={item.id} className="hover:bg-surface-container-low transition-colors">
      <td className="py-space-md px-space-base font-code-sm text-code-sm font-semibold text-on-surface">
        {item.inspection_code}
        <span className="block text-on-surface-variant font-normal">{dateObj ? dateObj.toLocaleDateString() : 'N/A'}</span>
      </td>
      <td className="py-space-md px-space-base">
        <div className="font-headline-sm text-headline-sm text-on-surface">{item.product_name_ai || 'Unknown Product'}</div>
      </td>
      <td className="py-space-md px-space-base">
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-label-sm text-label-sm font-semibold ${
          isNonCompliant ? 'text-error bg-error-container/30' : 'text-secondary bg-secondary-container/50'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isNonCompliant ? 'bg-error' : 'bg-secondary'}`}></span>
          {item.compliance_status || 'PENDING'}
        </span>
      </td>
      <td className="py-space-md px-space-base">
        {isNonCompliant ? (
          <div className="text-error font-medium">{item.violation_count} Violations</div>
        ) : (
          <div className="text-on-surface font-medium">All Declarations Verified</div>
        )}
      </td>
      <td className="py-space-md px-space-base text-right">
        <Link to={`/app/inspection/${item.id}`} className="px-space-sm py-1 bg-primary text-on-primary font-label-sm text-label-sm rounded hover:bg-surface-container-highest/80 hover:text-on-surface transition-colors inline-block">
          View Dossier
        </Link>
      </td>
    </tr>
  );
})}
</tbody>
</table>
</div>
<div className="p-space-base bg-surface-container-low/30 flex items-center justify-between font-body-sm text-body-sm text-on-surface-variant">
<span className="">Showing 4 of 14 audited products</span>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-1 bg-surface-container text-on-surface rounded disabled:opacity-50" disabled>Previous</button>
<button className="px-space-sm py-1 bg-surface-container hover:bg-surface-container-high text-on-surface rounded">Next</button>
</div>
</div>
</div>
</div>
{/*  Secondary Sidebar Column: Cross-Manufacturer Entity Directory (4 of 12 Cols)  */}
<div className="xl:col-span-4 flex flex-col space-y-space-base min-w-0">
{/*  Directory Control Card  */}
<div className="bg-surface-container-lowest rounded shadow-sm p-space-base flex flex-col space-y-space-base">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<Icon name="corporate_fare" className="text-secondary text-[20px]" />
<h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold">Entity Directory</h3>
</div>
<span className="font-code-sm text-code-sm text-on-surface-variant">Sector: Packaged Foods</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">
          Frequent manufacturers and brand accounts currently subject to recurring monitoring or periodic statutory calibration.
        </p>
</div>

{isLoading ? (
  <div className="text-center py-4 text-on-surface-variant text-sm">Loading offenders...</div>
) : (
  offenders.map(offender => (
    <div 
      key={offender.manufacturer_id} 
      onClick={() => setActiveOffender(offender)}
      className={`bg-surface-container-lowest hover:bg-surface-container-low transition-colors p-space-base rounded shadow-sm space-y-space-xs cursor-pointer ${
        activeOffender?.manufacturer_id === offender.manufacturer_id ? 'border-l-4 border-l-primary' : ''
      }`}
    >
      <div className="flex items-start justify-between">
      <span className="font-headline-sm text-headline-sm text-on-surface font-semibold leading-tight">
                  {offender.manufacturer_name}
                </span>
      <span className={`px-space-xs py-0.5 rounded font-label-sm text-label-sm shrink-0 ${
        offender.repeat_violation_count > 0 ? 'bg-error-container text-on-error-container' : 'bg-surface-container text-on-surface-variant font-medium'
      }`}>
                  {offender.repeat_violation_count > 0 ? 'Active Deficit' : 'Compliant'}
                </span>
      </div>
      <div className="font-body-sm text-body-sm text-on-surface-variant">
                Total Inspections: {offender.total_inspections}
              </div>
      <div className="pt-space-xs flex items-center justify-between font-code-sm text-code-sm text-on-surface">
      <span className="">Violations: <strong className={offender.total_violations > 0 ? 'text-error' : 'text-secondary'}>{offender.total_violations}</strong></span>
      <Icon name="arrow_forward" className={`text-[16px] ${activeOffender?.manufacturer_id === offender.manufacturer_id ? 'text-primary' : 'text-outline'}`} />
      </div>
    </div>
  ))
)}
{/*  Enforcement Framework Notice Panel  */}
<div className="bg-surface-container-high/40 p-space-base rounded space-y-space-xs">
<div className="flex items-center gap-space-xs text-on-surface">
<Icon name="gavel" className="text-[18px] text-secondary" />
<span className="font-label-md text-label-md font-semibold">Standard Operating Threshold</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant">
          Under Legal Metrology (Packaged Commodities) Rules, 2011, repeating typographic deficits across separate production batches trigger automated officer audit reminders. Labels are cataloged objectively without administrative presumption.
        </p>
</div>
</div>
</div>
</div>
  );
};

export default ManufacturerRepeat;
