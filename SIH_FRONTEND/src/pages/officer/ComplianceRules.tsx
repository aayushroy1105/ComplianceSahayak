import React, { useState } from 'react';
import Icon from '../../components/ui/Icon';

const ComplianceRules: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Example rule selection state
  const [selectedRuleId, setSelectedRuleId] = useState('rule-6-1-h');

  // Modal State
  const [modalState, setModalState] = useState<{ type: string, rule: any, result?: string } | null>(null);

  const ruleData = {
    'rule-6-1-a': {
      title: 'Rule 6(1)(a) — Name & Address',
      spec: 'Entity Extraction & PIN Resolution',
      passLogic: 'Physical street address along with 6-digit postal code identified with >90% OCR certainty score.',
      citation: 'Legal Metrology (Packaged Commodities) Rules, 2011, Chapter II, Rule 6, Sub-rule (1), Clause (a).',
      tolerance: 'Regex Exact Match Required',
      resolution: 'Document-level NLP'
    },
    'rule-6-1-h': {
      title: 'Rule 6(1)(h) & Sched. II',
      spec: 'Auto-detected PDP Area Scaling',
      passLogic: 'All mandatory numerals > statutory height threshold for calculated panel area.',
      citation: 'Legal Metrology (Packaged Commodities) Rules, 2011, GSR 202(E) dated 07 March 2011, as amended by GSR 779(E).',
      tolerance: '± 0.05 mm Mechanical',
      resolution: '≥ 300 DPI Raw Capture'
    },
    'rule-6-1-e': {
      title: 'Rule 6(1)(e) — Contact Channels',
      spec: 'Multi-Channel Availability',
      passLogic: 'At least one functioning contact method (Phone, Email, Physical Address) verified actively.',
      citation: 'Legal Metrology (Packaged Commodities) Rules, 2011, Section 6, sub-clause 1(e).',
      tolerance: 'Pattern Validation',
      resolution: 'Cross-verification API Check'
    },
    'rule-6-1-f': {
      title: 'Rule 6(1)(f) — MRP Format',
      spec: 'Currency String Parsing',
      passLogic: 'Contains standard prefix "MRP", "Max Retail Price", followed by valid numeric currency string.',
      citation: 'Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6, inclusive of tax provisions.',
      tolerance: 'Strict Syntax Check',
      resolution: 'OCR & Bounding Box Contrast'
    },
    'rule-6-1-m': {
      title: 'Rule 6(1)(m) — USP Unit Standard',
      spec: 'Volumetric & Mass Normalization',
      passLogic: 'Unit sale price is calculated and presented correctly matching standard volume or weight base unit.',
      citation: 'Legal Metrology (Packaged Commodities) Amendment Rules, 2022.',
      tolerance: 'Arithmetic Verification',
      resolution: 'Numeric Calculation Engine'
    }
  };

  const selectedRule = ruleData[selectedRuleId as keyof typeof ruleData];



  return (
    <div className="flex flex-col w-full">
      {/* Top Action & Meta Stream */}
      <div className="py-space-base px-space-base md:px-space-xl flex flex-col gap-space-md">
        {/* Breadcrumb & Mode Strip */}
        <div className="flex flex-wrap items-center justify-between gap-space-sm">
          <div className="flex items-center gap-space-xs font-code-sm text-[11px] font-medium text-slate-500 font-mono">
            <span className="text-slate-800">Officer Portal</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-800">Regulatory Reference</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-900 font-bold">Statutory Ruleset</span>
          </div>
          <div className="flex items-center gap-2 bg-slate-100 px-2.5 py-1 rounded border border-slate-200">
            <Icon name="info" className="text-[14px] text-slate-500" />
            <span className="font-mono text-[11px] text-slate-600 font-medium">Reference: LM-PCR-2011</span>
          </div>
        </div>

        {/* Page Title & Authority Descriptor */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base">
          <div className="max-w-3xl">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Statutory Reference Catalogue</h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-4xl leading-relaxed">
              Reference catalogue for legal metrology checkpoints and verification heuristics. Note: This is an informational catalogue; actual enforcement rules are queried dynamically by the AI engine.
            </p>
          </div>
          {/* Quick Metric Counter */}
          <div className="flex items-center gap-4 bg-slate-50 p-3 rounded-lg shadow-sm border border-slate-200/60">
            <div className="flex flex-col pr-4 border-r border-slate-200">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold font-mono">Deterministic Checks</span>
              <span className="text-lg text-slate-900 font-bold">18 Rules</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold font-mono">Schedule Mappings</span>
              <span className="text-lg text-slate-900 font-bold">II, III &amp; VI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search & Regulatory Navigation Surface */}
      <div className="px-space-base md:px-space-xl pb-space-lg">
        <div className="bg-white p-4 rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col gap-4">
          {/* Search Field with Calibration Visual */}
          <div className="relative w-full">
            <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[20px]" />
            <input 
              className="w-full pl-10 pr-4 py-2 text-slate-900 placeholder:text-slate-400 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-slate-900 focus:bg-white transition-all" 
              placeholder="Search statutory rules, sections, or keywords (e.g., numeral height, MRP, net quantity)..." 
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:flex items-center gap-1 font-mono text-[10px] text-slate-500 bg-white border border-slate-200 px-1.5 py-0.5 rounded shadow-sm">
              <span>Alt</span><span>+</span><span>K</span>
            </div>
          </div>
          {/* Categories / Tab Channels */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            <button 
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${activeFilter === 'all' ? 'bg-slate-900 text-white shadow-sm' : 'bg-slate-50 text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
              onClick={() => setActiveFilter('all')}
            >
              All Rules
            </button>
            <button 
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${activeFilter === 'mandatory' ? 'bg-slate-900 text-white shadow-sm' : 'bg-slate-50 text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
              onClick={() => setActiveFilter('mandatory')}
            >
              Sec 6 Mandatory Declarations
            </button>
            <button 
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${activeFilter === 'sizing' ? 'bg-slate-900 text-white shadow-sm' : 'bg-slate-50 text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
              onClick={() => setActiveFilter('sizing')}
            >
              Schedule II Font &amp; Numeral Sizing
            </button>
            <button 
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${activeFilter === 'packaging' ? 'bg-slate-900 text-white shadow-sm' : 'bg-slate-50 text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
              onClick={() => setActiveFilter('packaging')}
            >
              Schedule III Quantities
            </button>
          </div>
        </div>
      </div>

      {/* Workspace Grid: Rule Catalog & Dynamic Applicability Matrix */}
      <div className="px-space-base md:px-space-xl pb-10 grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Rule Cards Catalog (xl:col-span-8) */}
        <div className="xl:col-span-8 flex flex-col gap-4">
          
          {/* Card 1: Manufacturer & Packer Identification */}
          <div 
            className={`bg-white border rounded-xl p-5 md:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-all cursor-pointer group ${selectedRuleId === 'rule-6-1-a' ? 'border-slate-800 ring-1 ring-slate-800' : 'border-slate-200/80'}`}
            onClick={() => setSelectedRuleId('rule-6-1-a')}
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-700 bg-slate-100 px-2 py-0.5 rounded font-semibold border border-slate-200">
                  <Icon name="gavel" className="text-[15px]" />
                  <span>PCR 2011 · Rule 6(1)(a)</span>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200/50 rounded text-[10px] font-bold uppercase tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                  <span>Statutory Mandatory</span>
                </div>
              </div>
              <h2 className="text-lg font-bold text-slate-900 group-hover:text-slate-700 transition-colors">
                Name &amp; Complete Address of Manufacturer / Packer / Importer
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                Standard: Clear physical registered premises address required on principal or secondary panel. For imported goods, country of origin along with importer name &amp; registered postal code must be unambiguously stated.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Statutory Scope</span>
                  <span className="text-xs text-slate-800 font-semibold">All Pre-Packaged Commodities</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Automated Engine</span>
                  <span className="text-xs text-slate-800 font-semibold">OCR Entity Extraction + PIN Registry Cross-check</span>
                </div>
              </div>
              <div className="flex items-center justify-between pt-2 text-slate-500 text-xs font-mono">
                <span className="flex items-center gap-1.5">
                  <Icon name="visibility" className="text-[16px]" />
                  <span>Confidence Threshold: ≥92.0%</span>
                </span>
                <span className="text-slate-600 font-semibold flex items-center gap-1 cursor-pointer hover:text-slate-900 transition-colors" onClick={(e) => { e.stopPropagation(); setModalState({ type: 'deterministic', rule: ruleData['rule-6-1-a'] }); }}>
                  <span>View Deterministic Model</span>
                  <Icon name="arrow_forward" className="text-[16px]" />
                </span>
              </div>
            </div>
          </div>

          {/* Card 2: Font & Numeral Sizing Calibration Table (Schedule II) */}
          <div 
            className={`bg-white border rounded-xl p-5 md:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-all cursor-pointer group ${selectedRuleId === 'rule-6-1-h' ? 'border-slate-800 ring-1 ring-slate-800' : 'border-slate-200/80'}`}
            onClick={() => setSelectedRuleId('rule-6-1-h')}
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-700 bg-slate-100 px-2 py-0.5 rounded font-semibold border border-slate-200">
                  <Icon name="straighten" className="text-[15px]" />
                  <span>PCR 2011 · Rule 6(1)(h) &amp; Sched. II</span>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200/50 rounded text-[10px] font-bold uppercase tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
                  <span>Geometric Verification</span>
                </div>
              </div>
              <h2 className="text-lg font-bold text-slate-900 group-hover:text-slate-700 transition-colors">
                Minimum Height of Numerals &amp; Letters on Principal Display Panel
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                Standard: Explicit numeral height scaling strictly linked to Principal Display Panel (PDP) net surface area calculation. Mandatory baseline for Net Quantity, MRP, and Date markings.
              </p>
              
              {/* Structured Numeral Calibration Matrix */}
              <div className="overflow-x-auto rounded-lg bg-slate-50 border border-slate-200 p-1 mt-2">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="font-mono text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-200">
                      <th className="p-2 font-semibold">PDP Area Bracket</th>
                      <th className="p-2 font-semibold">Standard Packaging (Req)</th>
                      <th className="p-2 font-semibold">Blown / Moulded / Perforated</th>
                      <th className="p-2 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-[11px] text-slate-800 divide-y divide-slate-100">
                    <tr className="hover:bg-slate-100 transition-colors">
                      <td className="p-2 font-medium">Area ≤ 50 cm²</td>
                      <td className="p-2">≥ 1.0 mm</td>
                      <td className="p-2">≥ 1.5 mm</td>
                      <td className="p-2 text-emerald-700 font-semibold">Active Matrix</td>
                    </tr>
                    <tr className="hover:bg-slate-100 transition-colors">
                      <td className="p-2 font-medium">50 cm² &lt; Area ≤ 100 cm²</td>
                      <td className="p-2">≥ 1.5 mm</td>
                      <td className="p-2">≥ 2.0 mm</td>
                      <td className="p-2 text-emerald-700 font-semibold">Active Matrix</td>
                    </tr>
                    <tr className="hover:bg-slate-100 transition-colors">
                      <td className="p-2 font-medium">100 cm² &lt; Area ≤ 500 cm²</td>
                      <td className="p-2">≥ 2.0 mm</td>
                      <td className="p-2">≥ 4.0 mm</td>
                      <td className="p-2 text-emerald-700 font-semibold">Active Matrix</td>
                    </tr>
                    <tr className="hover:bg-slate-100 transition-colors">
                      <td className="p-2 font-medium">Area &gt; 500 cm²</td>
                      <td className="p-2">≥ 4.0 mm</td>
                      <td className="p-2">≥ 6.0 mm</td>
                      <td className="p-2 text-emerald-700 font-semibold">Active Matrix</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div className="flex items-center justify-between pt-2 text-slate-500 text-xs font-mono">
                <span className="flex items-center gap-1.5">
                  <Icon name="aspect_ratio" className="text-[16px]" />
                  <span>Optical DPI Calibrator: Active (1:1 Metric Scale)</span>
                </span>
                <span className="text-slate-600 font-semibold flex items-center gap-1 cursor-pointer hover:text-slate-900 transition-colors" onClick={(e) => { e.stopPropagation(); setModalState({ type: 'geometric', rule: ruleData['rule-6-1-h'] }); }}>
                  <span>View Geometric Formula</span>
                  <Icon name="arrow_forward" className="text-[16px]" />
                </span>
              </div>
            </div>
          </div>

          {/* Card 3: Consumer Care Grievance Redressal */}
          <div 
            className={`bg-white border rounded-xl p-5 md:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-all cursor-pointer group ${selectedRuleId === 'rule-6-1-e' ? 'border-slate-800 ring-1 ring-slate-800' : 'border-slate-200/80'}`}
            onClick={() => setSelectedRuleId('rule-6-1-e')}
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-700 bg-slate-100 px-2 py-0.5 rounded font-semibold border border-slate-200">
                  <Icon name="contact_support" className="text-[15px]" />
                  <span>PCR 2011 · Rule 6(1)(e)</span>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200/50 rounded text-[10px] font-bold uppercase tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                  <span>Consumer Protection</span>
                </div>
              </div>
              <h2 className="text-lg font-bold text-slate-900 group-hover:text-slate-700 transition-colors">
                Consumer Care &amp; Grievance Redressal Mandatory Contact Channels
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                Standard: Mandatory name, address, valid reachable telephone/helpline number, and official corporate grievance email address on every package for consumer feedback or complaint lodging.
              </p>
              <div className="flex flex-wrap gap-2 pt-2">
                <span className="px-2 py-1 bg-slate-50 border border-slate-200 rounded font-mono text-[11px] text-slate-700">
                  ✓ Designated Officer / Cell
                </span>
                <span className="px-2 py-1 bg-slate-50 border border-slate-200 rounded font-mono text-[11px] text-slate-700">
                  ✓ Working Telephony Format
                </span>
                <span className="px-2 py-1 bg-slate-50 border border-slate-200 rounded font-mono text-[11px] text-slate-700">
                  ✓ RFC 5322 Validated Email Regex
                </span>
              </div>
              <div className="flex items-center justify-between pt-2 text-slate-500 text-xs font-mono">
                <span className="flex items-center gap-1.5">
                  <Icon name="verified" className="text-[16px]" />
                  <span>Parser Confidence: Multi-channel Regex Verified</span>
                </span>
                <span className="text-slate-600 font-semibold flex items-center gap-1 cursor-pointer hover:text-slate-900 transition-colors" onClick={(e) => { e.stopPropagation(); setModalState({ type: 'declaration', rule: ruleData['rule-6-1-e'] }); }}>
                  <span>View Declaration Details</span>
                  <Icon name="arrow_forward" className="text-[16px]" />
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Rule Detail / Technical Applicability Drawer (xl:col-span-4) */}
        <div className="xl:col-span-4 flex flex-col gap-6 lg:sticky lg:top-20">
          
          {/* Interactive Selected Parameter Inspector Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col gap-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex flex-col">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Deterministic Spec</span>
                <h3 className="text-lg text-slate-900 font-bold">{selectedRule?.title || 'Rule Details'}</h3>
              </div>
              <Icon name="tune" className="text-slate-400 text-[24px]" />
            </div>
            
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-xs text-slate-500 uppercase tracking-wider font-mono">Optical Measurement Criteria</span>
              <div className="bg-slate-50 border border-slate-200 p-3 rounded-lg space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Bounding Box Minimum:</span>
                  <span className="font-mono text-[11px] font-semibold text-slate-800">{selectedRule?.spec}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Optical Resolution:</span>
                  <span className="font-mono text-[11px] font-semibold text-slate-800">{selectedRule?.resolution}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Tolerance Allowance:</span>
                  <span className="font-mono text-[11px] font-semibold text-slate-800">{selectedRule?.tolerance}</span>
                </div>
              </div>
            </div>

            {/* Deterministic Test Logic Breakdown */}
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-xs text-slate-500 uppercase tracking-wider font-mono">Automated Pass / Fail Criteria</span>
              <div className="space-y-1.5 font-mono text-[11px]">
                <div className="p-2 rounded bg-emerald-50/50 border border-emerald-100 flex items-start gap-2 text-slate-700">
                  <Icon name="check_circle" className="text-[16px] text-emerald-600 mt-0.5" />
                  <span className="leading-snug">{selectedRule?.passLogic}</span>
                </div>
                <div className="p-2 rounded bg-rose-50/50 border border-rose-100 flex items-start gap-2 text-slate-700">
                  <Icon name="cancel" className="text-[16px] text-rose-600 mt-0.5" />
                  <span className="leading-snug">Any violation of the above constraint generates flagged dossier infraction for adjudicator review.</span>
                </div>
              </div>
            </div>

            {/* Statutory Gazette Citations */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex flex-col gap-1.5">
              <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Gazette Regulatory Anchor</span>
              <p className="text-xs text-slate-700 leading-relaxed">
                {selectedRule?.citation}
              </p>
            </div>

          </div>

          {/* Institutional Ingestion & Rules Engine Note Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-2">
            <div className="flex items-center gap-1.5 text-slate-700 text-sm font-semibold">
              <Icon name="dataset" className="text-[18px]" />
              <span>Rules Engine Integration</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Statutory rules are loaded from the active Legal Metrology Rules Engine configuration. New amendments can be ingested via regulatory rule definitions.
            </p>
            <div className="pt-1 flex items-center justify-between font-mono text-[10px] text-slate-500">
              <span>Engine Sync: Validated</span>
              <span className="font-semibold text-slate-800">v2.4.12-PROD</span>
            </div>
          </div>

        </div>
      </div>

      {modalState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" onClick={() => setModalState(null)}>
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-slate-900">Rule Details</h3>
              <button onClick={() => setModalState(null)} className="text-slate-400 hover:text-slate-700">
                <Icon name="close" className="text-[24px]" />
              </button>
            </div>
            <div className="space-y-4">
              <p className="font-semibold text-slate-800">{modalState.rule?.title}</p>
              <p className="text-slate-600 text-sm">{modalState.rule?.passLogic}</p>
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase">Citation</h4>
                <p className="text-sm text-slate-800 mt-1">{modalState.rule?.citation}</p>
              </div>
              <p className="text-slate-500 text-xs">Resolution: {modalState.rule?.resolution} | Tolerance: {modalState.rule?.tolerance}</p>
            </div>
            <div className="mt-6 flex justify-end">
              <button onClick={() => setModalState(null)} className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceRules;
