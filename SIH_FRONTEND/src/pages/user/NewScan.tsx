import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';

type AngleType = 'FRONT' | 'BACK' | 'SIDE' | 'OTHER';
interface UploadedAngle {
  file: File;
  previewUrl: string;
  type: AngleType;
  id: string;
}

const NewScan: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const pendingAngleRef = useRef<AngleType>('FRONT');
  const [angles, setAngles] = useState<UploadedAngle[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<'idle' | 'creating' | 'uploading' | 'analyzing' | 'done'>('idle');
  const [inspectionId, setInspectionId] = useState<string | null>(null);
  const [uploadedAngleIds, setUploadedAngleIds] = useState<Set<string>>(new Set());

  const initiateUpload = (type: AngleType) => {
    pendingAngleRef.current = type;
    fileInputRef.current?.click();
  };

  const handleReset = () => {
    angles.forEach(a => URL.revokeObjectURL(a.previewUrl));
    setAngles([]);
    setError(null);
    setWorkflowStatus('idle');
    setInspectionId(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Invalid file type. Only JPEG, PNG, and WEBP are allowed.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB limit.');
      return;
    }

    setError(null);
    const newAngle: UploadedAngle = {
      file,
      previewUrl: URL.createObjectURL(file),
      type: pendingAngleRef.current,
      id: Math.random().toString(36).substring(7)
    };
    
    setAngles(prev => [...prev, newAngle]);
    // Reset file input so same file can be uploaded again if needed
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleStartAnalysis = async () => {
    if (angles.length === 0) {
      setError('Please select at least one package image.');
      return;
    }

    setError(null);
    let currentInspectionId = inspectionId;

    try {
      if (!currentInspectionId) {
        setWorkflowStatus('creating');
        const createRes = await inspectionsApi.createInspection({});
        currentInspectionId = createRes.id;
        setInspectionId(currentInspectionId);
      }

      setWorkflowStatus('uploading');
      for (const angle of angles) {
        if (!uploadedAngleIds.has(angle.id)) {
          await inspectionsApi.uploadImage(currentInspectionId, angle.file, angle.type);
          setUploadedAngleIds(prev => new Set(prev).add(angle.id));
        }
      }

      setWorkflowStatus('analyzing');
      await inspectionsApi.analyze(currentInspectionId);

      setWorkflowStatus('done');
      navigate(`/app/user/reports/${currentInspectionId}`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unexpected error occurred';
      // Depending on state, workflowStatus might not reflect current fail point perfectly due to closure, 
      // but it does since it's set right before await. Wait, React state isn't synchronous.
      // Better to track in a local variable or just say "Operation failed".
      setError(`Operation failed: ${errorMessage}`);
      setWorkflowStatus('idle');
    }
  };

  return (
    <div className="flex flex-col w-full pb-10">
      {/* Operational Header Strip (User Workspace Identity) */}
      <div className="w-full bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 rounded-xl px-4 sm:px-6 py-4 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-slate-50 flex items-center justify-center p-1 border border-slate-100 shadow-sm">
            <img alt="ComplianceSahayak Platform Seal" className="h-full w-full object-contain opacity-70 grayscale" src="/brand/compliancesahayak-logo.png" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xl font-bold text-slate-900 tracking-tight">Initiate Package Verification</span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 font-semibold">New Scan</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Upload packaging images and provide details for compliance verification.</p>
          </div>
        </div>
        <div className="flex items-center gap-4 self-start md:self-auto">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-100">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
            </span>
            <span className="text-xs text-slate-700 font-bold">System Operational</span>
          </div>
          <div className="h-6 w-px bg-slate-200 hidden sm:block"></div>
          <div className="flex items-center gap-2 text-slate-700">
            <Icon name="account_circle" className="text-[20px] text-slate-400" />
            <div className="flex flex-col">
              <span className="text-[11px] text-slate-900 font-bold leading-none">QA Lead</span>
              <span className="font-mono text-[9px] text-slate-500 mt-0.5">User Account — Quality Lead</span>
            </div>
          </div>
        </div>
      </div>

      {/* Inspection Workflow Stepper */}
      <div className="w-full bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
          {/* Step 1 (Active) */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200 transition-all">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-sm shrink-0">
              1
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-bold text-slate-900 truncate">Upload Package Images</span>
              <span className={`font-mono text-[10px] font-semibold ${angles.length > 0 ? 'text-emerald-600' : 'text-slate-500'}`}>
                {angles.length > 0 ? `${angles.length} Angle${angles.length !== 1 ? 's' : ''} Uploaded` : 'Pending Upload'}
              </span>
            </div>
            <Icon name="radio_button_checked" className="text-slate-900 text-[20px] ml-auto shrink-0" />
          </div>
          {/* Step 2 */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white border border-transparent hover:border-slate-100 transition-all">
            <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center font-bold text-sm shrink-0 border border-slate-200">
              2
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-bold text-slate-500 truncate">Package Details</span>
              <span className="font-mono text-[10px] text-slate-400 font-medium">OCR Field Auto-Extracted</span>
            </div>
            <Icon name="auto_fix_high" className="text-slate-300 text-[20px] ml-auto shrink-0" />
          </div>
          {/* Step 3 */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white border border-transparent hover:border-slate-100 transition-all">
            <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center font-bold text-sm shrink-0 border border-slate-200">
              3
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-bold text-slate-500 truncate">Run Compliance Analysis</span>
              <span className="font-mono text-[10px] text-slate-400 font-medium">Statutory PCR Matrix</span>
            </div>
            <Icon name="gavel" className="text-slate-300 text-[20px] ml-auto shrink-0" />
          </div>
        </div>
      </div>

      {/* Main Workstation Layout: Responsive Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Package Image Capture & Multi-Angle Repository (7 cols desktop) */}
        <div className="lg:col-span-7 flex flex-col gap-6 w-full min-w-0">
          
          {/* Primary Dropzone / Viewport */}
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon name="add_photo_alternate" className="text-slate-700 text-[20px]" />
                <span className="text-base font-bold text-slate-900">Optical Evidence Ingestion</span>
              </div>
              <span className="font-mono text-[10px] bg-slate-50 border border-slate-200 px-2 py-0.5 rounded text-slate-500 font-semibold">Image upload</span>
            </div>
            
            {/* Interactive Drag & Drop Box */}
            <input type="file" ref={fileInputRef} className="hidden" accept="image/jpeg, image/png, image/webp" onChange={handleFileSelect} />
            {angles.length === 0 ? (
              <div className="group relative w-full rounded-xl bg-slate-50 border-2 border-dashed border-slate-200 p-6 sm:p-8 flex flex-col items-center justify-center text-center shadow-inner">
                <div className="w-14 h-14 rounded-full bg-white shadow-sm border border-slate-100 flex items-center justify-center text-slate-500 mb-3">
                  <Icon name="cloud_upload" className="text-[30px]" />
                </div>
                <span className="text-sm font-bold text-slate-900 mb-1">Upload Packaging Images</span>
                <p className="text-xs text-slate-500 max-w-md mb-4 leading-relaxed">Select an angle to upload for compliance verification.</p>
                <div className="flex flex-wrap items-center justify-center gap-3">
                  {(['FRONT', 'BACK', 'SIDE', 'OTHER'] as AngleType[]).map(type => (
                    <button 
                      key={type}
                      type="button"
                      className="px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition-colors shadow-sm flex items-center gap-1.5 focus:outline-none" 
                      onClick={() => initiateUpload(type)}
                    >
                      <Icon name="add_photo_alternate" className="text-[16px]" />
                      <span>Add {type}</span>
                    </button>
                  ))}
                </div>
                <div className="mt-4 flex items-center gap-3 text-slate-400 font-mono text-[10px] font-medium">
                  <span>Formats: JPEG, PNG, WEBP</span>
                  <span className="text-slate-300">•</span>
                  <span>Max size: 5MB/file</span>
                </div>
              </div>
            ) : null}
            {error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 mt-2">
                <Icon name="error" className="text-rose-500 text-[18px] shrink-0 mt-0.5" />
                <span className="text-sm font-semibold">{error}</span>
              </div>
            )}

            {/* Section Info Pill */}
            <div className="flex items-start gap-2 p-3 rounded-lg bg-slate-50 border border-slate-100 text-slate-700">
              <Icon name="info" className="text-slate-400 text-[18px] shrink-0 mt-0.5" />
              <span className="text-[11px] leading-relaxed">Images will be analyzed for package declarations and compliance indicators. For best results, ensure packaging surfaces are clearly illuminated.</span>
            </div>
          </div>

          {/* Uploaded Image Preview Gallery & Calibrated Surface Cards */}
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Icon name="layers" className="text-slate-700 text-[20px]" />
                <span className="text-base font-bold text-slate-900">Package Angles</span>
                {angles.length > 0 && (<span className="font-mono text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 font-bold ml-1">{angles.length} Uploaded</span>)}
              </div>
              <span className="font-mono text-[10px] text-slate-500 font-medium">Ready for Upload</span>
            </div>
            
            {/* Grid of Inspection Images */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {angles.map(angle => (
                <div key={angle.id} className="bg-slate-50 rounded-xl p-2 border border-slate-200 flex flex-col gap-2 shadow-sm transition-all hover:bg-slate-100">
                  <div className="relative w-full aspect-[4/3] rounded-lg overflow-hidden bg-slate-200 flex items-center justify-center">
                    <img alt={angle.type} className="w-full h-full object-cover" src={angle.previewUrl} />
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-sm text-white font-mono text-[10px] flex items-center gap-1.5 shadow-sm">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      <span>{angle.type}</span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 px-1.5 pb-1 mt-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] text-slate-900 font-bold">{angle.type} Panel</span>
                      <span className="font-mono text-[9px] px-1 py-0.5 rounded font-semibold text-emerald-700 bg-emerald-100/50 border border-emerald-200">
                        Ready
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-200 mt-1">
                      <button className="text-slate-400 hover:text-slate-600 text-[10px] font-bold flex items-center gap-1 py-1 focus:outline-none cursor-not-allowed" disabled type="button">
                        <Icon name="crop_rotate" className="text-[14px]" />
                        <span>Adjust (N/A)</span>
                      </button>
                      <button 
                        className="text-rose-600 hover:text-rose-800 text-[10px] font-bold py-1 focus:outline-none" 
                        onClick={() => {
                          setAngles(prev => prev.filter(a => a.id !== angle.id));
                          URL.revokeObjectURL(angle.previewUrl);
                        }}
                        type="button"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {angles.length > 0 && (
                <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-4 flex flex-col items-center justify-center text-center opacity-80 min-h-[190px]">
                  <span className="text-xs font-bold text-slate-700 mb-3">Add Another Angle</span>
                  <div className="grid grid-cols-2 gap-2 w-full max-w-[200px]">
                    {(['FRONT', 'BACK', 'SIDE', 'OTHER'] as AngleType[]).map(type => (
                      <button 
                        key={type}
                        type="button"
                        className="px-2 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-[10px] font-bold hover:bg-slate-100 transition-colors shadow-sm focus:outline-none" 
                        onClick={() => initiateUpload(type)}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Product Context & Compliance Execution (5 cols desktop) */}
        <div className="lg:col-span-5 flex flex-col gap-6 w-full min-w-0">
          
          {/* Section 2: Product Context (Simple & Non-intimidating) */}
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon name="fact_check" className="text-slate-700 text-[20px]" />
                <h2 className="text-base font-bold text-slate-900">Product Context</h2>
              </div>
              <span className="font-mono text-[10px] bg-slate-50 border border-slate-200 px-2 py-0.5 rounded text-slate-500 font-semibold">Image upload</span>
            </div>
            
            {/* Helpful friendly note */}
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-start gap-2">
              <Icon name="auto_awesome" className="text-slate-400 text-[18px] shrink-0 mt-0.5" />
              <p className="text-xs text-slate-600 leading-relaxed">Detected packaging information is populated below. You can review or adjust before analyzing.</p>
            </div>
            
            {/* Form fields container */}
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Extracted packaging text</span>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-900 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs">Brand &amp; Product</span>
                    <span className="font-mono text-[11px] text-slate-600 font-medium">Pending Analysis</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs">Net Quantity</span>
                    <span className="font-mono text-[11px] text-slate-600 font-medium">-</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs">MRP Declaration</span>
                    <span className="font-mono text-[11px] text-slate-600 font-medium">-</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between text-slate-500 font-mono text-[10px] pt-3 border-t border-slate-200 font-medium">
                <span>Status: Ready for analysis</span>
                <span>Verification Mode: Standard</span>
              </div>
            </div>
          </div>

          {/* Section 3: Pre-Scan Summary & Analysis Trigger */}
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 flex flex-col gap-4">
            
            {/* Verification Readiness Status Header */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 shadow-sm">
                <Icon name="checklist_rtl" className="text-[20px]" />
              </div>
              <div className="flex flex-col">
                <span className="text-base font-bold text-slate-900 leading-tight">Ready to Analyze</span>
                <span className="text-[11px] text-slate-500 mt-0.5">Evaluation standard: LM(PC) Rules</span>
              </div>
            </div>
            
            {/* Summary Metric Card */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200/60">
                <span className="text-xs font-bold text-slate-900">Audit Prerequisites</span>
                <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-emerald-100/50 border border-emerald-200 text-emerald-800 font-bold">Ready to Scan</span>
              </div>
              <ul className="flex flex-col gap-2.5 text-slate-700 text-xs">
                <li className="flex items-start gap-2">
                  <Icon name={angles.length > 0 ? 'check_circle' : 'circle'} className={`${angles.length > 0 ? 'text-emerald-600' : 'text-slate-300'} text-[16px] shrink-0 mt-0.5`} />
                  <span className="leading-snug"><strong>{angles.length} package angle{angles.length !== 1 ? 's' : ''} uploaded</strong> (PDP)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Icon name={angles.length > 0 ? 'check_circle' : 'circle'} className={`${angles.length > 0 ? 'text-emerald-600' : 'text-slate-300'} text-[16px] shrink-0 mt-0.5`} />
                  <span className="leading-snug"><strong>Image format supported</strong></span>
                </li>
                <li className="flex items-start gap-2">
                  <Icon name={angles.length > 0 ? 'check_circle' : 'circle'} className={`${angles.length > 0 ? 'text-emerald-600' : 'text-slate-300'} text-[16px] shrink-0 mt-0.5`} />
                  <span className="leading-snug"><strong>Ready for analysis</strong></span>
                </li>
              </ul>
              <div className="mt-1 pt-3 flex items-center justify-between text-slate-500 font-mono text-[10px] border-t border-slate-200/60 font-medium">
                <span>Status: {angles.length > 0 ? 'Ready for analysis' : 'Pending Upload'}</span>
                <span>Verification Mode: Standard</span>
              </div>
            </div>

            {/* Action Trigger Group */}
            <div className="flex flex-col gap-3 pt-2">
              {/* Primary CTA Button */}
              <button 
                className={`w-full min-h-[48px] py-3 px-6 rounded-xl bg-slate-900 text-white hover:bg-slate-800 active:scale-[0.99] transition-all text-sm font-bold flex items-center justify-center gap-2 shadow-sm focus:outline-none ${workflowStatus !== 'idle' || angles.length === 0 ? 'opacity-80 cursor-wait' : ''}`}
                onClick={handleStartAnalysis}
                disabled={workflowStatus !== 'idle' || angles.length === 0}
                type="button"
              >
                {workflowStatus !== 'idle' ? (
                  <>
                    <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    <span>
                      {workflowStatus === 'creating' && 'Creating Inspection...'}
                      {workflowStatus === 'uploading' && 'Uploading Image...'}
                      {workflowStatus === 'analyzing' && 'Analyzing Statutory Rules...'}
                      {workflowStatus === 'done' && 'Redirecting...'}
                    </span>
                  </>
                ) : (
                  <>
                    <Icon name="query_stats" className="text-[20px]" />
                    <span>Start Compliance Analysis &rarr;</span>
                  </>
                )}
              </button>
              
              {/* Secondary CTA Row */}
              <div className="grid grid-cols-2 gap-3">
                <button 
                  className="min-h-[44px] py-2.5 px-4 rounded-lg bg-slate-50 border border-slate-200 text-slate-400 text-xs font-bold transition-colors flex items-center justify-center gap-1.5 focus:outline-none cursor-not-allowed" 
                  disabled 
                  title="Saving draft is unsupported" 
                  type="button"
                >
                  <Icon name="bookmark_border" className="text-[16px]" />
                  <span>Save Draft</span>
                </button>
                <button 
                  className="min-h-[44px] py-2.5 px-4 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-xs font-bold hover:bg-slate-100 hover:text-slate-900 transition-colors flex items-center justify-center gap-1.5 focus:outline-none" 
                  onClick={handleReset}
                  type="button"
                >
                  <Icon name="restart_alt" className="text-[16px]" />
                  <span>Reset Fields</span>
                </button>
              </div>
            </div>
            
            {/* Prototype Boundary Assurance Footer */}
            <div className="pt-2 text-center">
              <span className="font-mono text-[10px] text-slate-400 font-medium">Status: {angles.length > 0 ? 'Ready for analysis' : 'Pending Upload'} • Verification Mode: Standard</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default NewScan;
