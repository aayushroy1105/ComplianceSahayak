import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { ApiError } from '../../api/types';

const NewInspection: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [locationText, setLocationText] = useState('retail');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('Image exceeds 5MB limit.');
      return;
    }
    // Validate type
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setErrorMsg('Only JPEG, PNG, and WebP are allowed.');
      return;
    }

    setErrorMsg(null);
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setFilePreviewUrl(url);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) {
      setErrorMsg('Please select a package image file before submitting intake.');
      return;
    }

    setIsSubmitting(true);
    let inspectionId = '';

    try {
      // 1. Create Inspection
      const createRes = await inspectionsApi.createInspection({
        location_text: locationText || 'Delhi NCR Field Zone',
        inspection_date: new Date().toISOString(),
      });
      inspectionId = createRes.id;

      // 2. Upload Image
      await inspectionsApi.uploadImage(inspectionId, selectedFile);

      // 3. Trigger Real AI Analysis Pipeline
      await inspectionsApi.analyze(inspectionId);

      // Success, go to Dossier
      navigate(`/app/inspection/${inspectionId}`);
    } catch (error) {
      const apiError = error as ApiError;
      setErrorMsg(`Failed: ${apiError.detail || apiError.message || 'Unknown error'}`);
      // If we failed after creation, we don't navigate, but we show the error.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col w-full pb-8 space-y-6">
      {/* Breadcrumb / Top Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-2 font-medium text-xs text-slate-500 flex-wrap">
          <span className="text-slate-700 font-medium">Officer Portal</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-900 font-semibold">New Inspection Intake</span>
        </div>
        <div className="flex items-center gap-3 self-start sm:self-auto">
          <span className="text-xs text-slate-600 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>LM Ruleset v4.2 Active
          </span>
          <div className="h-4 w-px bg-slate-200 hidden sm:block"></div>
          <span className="text-xs text-slate-500 font-medium">Calibrated Mode</span>
        </div>
      </div>

      {/* Header Area */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="relative z-10 space-y-1.5 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 rounded text-slate-700 text-xs font-semibold uppercase tracking-wider">
            <Icon name="verified_user" className="text-[15px]" />Package Inspection Protocol
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">New Package Inspection Intake</h1>
          <p className="text-xs sm:text-sm text-slate-500">Capture package evidence and intake metadata for compliance verification.</p>
          {errorMsg && (
            <div className="mt-2 p-3 bg-red-50 text-red-700 text-sm font-semibold border border-red-200 rounded-lg">
              {errorMsg}
            </div>
          )}
        </div>
        <div className="relative z-10 flex flex-col items-start md:items-end justify-center bg-slate-50 border border-slate-100 p-4 rounded-lg min-w-[220px]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Workflow Phase</span>
          <span className="text-base font-bold text-slate-900">Stage 1 of 3</span>
          <span className="text-xs text-slate-500 mt-1 flex items-center gap-1">
            <Icon name="tune" className="text-[14px]" /> Automatic Resolution Scale
          </span>
        </div>
      </div>

      {/* Stepper */}
      <div className="bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-slate-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50/70 border border-blue-200/60 transition-all">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-sm">1</div>
            <div className="flex flex-col min-w-0">
              <span className="font-bold text-slate-900 text-sm truncate">Evidence Capture</span>
              <span className="text-xs text-slate-500 truncate">Active Workspace</span>
            </div>
            <Icon name="radio_button_checked" className="text-blue-600 ml-auto text-[18px]" />
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200/80 transition-all opacity-50">
            <div className="w-8 h-8 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-sm">2</div>
            <div className="flex flex-col min-w-0">
              <span className="font-semibold text-slate-800 text-sm truncate">Analysis</span>
              <span className="text-xs text-slate-500 truncate">Pending Upload</span>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200/80 transition-all opacity-50">
            <div className="w-8 h-8 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-sm">3</div>
            <div className="flex flex-col min-w-0">
              <span className="font-semibold text-slate-800 text-sm truncate">Pre-Analysis Review</span>
              <span className="text-xs text-slate-500 truncate">Ready for Orchestration</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left Column: Image Capture */}
        <div className="xl:col-span-7 flex flex-col space-y-6">
          <div className="bg-white p-5 sm:p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <Icon name="photo_camera_back" className="text-slate-900 text-[20px]" />
                  <h2 className="font-bold text-base text-slate-900">Multi-Angle Package Canvas</h2>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">Ensure 90-degree orthogonal positioning under uniform ambient diffuse lighting.</p>
              </div>
              <div className="flex items-center gap-2 self-start sm:self-auto">
                <button className="px-3 py-1.5 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 border border-slate-200" type="button">
                  <Icon name="grid_on" className="text-[15px]" /> Grid Overlay
                </button>
                <button className="px-3 py-1.5 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 border border-slate-200" type="button">
                  <Icon name="crop" className="text-[15px]" /> Calibrate
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Single Image Upload Angle */}
              <div 
                className="bg-slate-50 rounded-xl p-3 flex flex-col justify-between space-y-2 border border-dashed border-slate-300 hover:bg-slate-100/70 transition-colors cursor-pointer group"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-xs text-slate-700 flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${selectedFile ? 'bg-emerald-500' : 'bg-slate-300'}`}></span> Front / Primary Display Panel
                  </span>
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold uppercase ${selectedFile ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-200 text-slate-700'}`}>
                    {selectedFile ? 'UPLOADED' : 'REQUIRED FOR TEST'}
                  </span>
                </div>
                
                {filePreviewUrl ? (
                  <div className="relative h-52 rounded-lg overflow-hidden bg-slate-100 flex items-center justify-center border border-slate-200">
                    <img className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" alt="Selected file preview" src={filePreviewUrl} />
                  </div>
                ) : (
                  <div className="h-52 rounded-lg bg-white border border-slate-200/80 flex flex-col items-center justify-center p-4 text-center space-y-2">
                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-700 group-hover:scale-110 transition-transform shadow-sm">
                      <Icon name="add_a_photo" className="text-[20px]" />
                    </div>
                    <div className="space-y-0.5">
                      <span className="font-bold text-xs text-slate-900 block">+ Add Package Image</span>
                      <p className="text-[11px] text-slate-500 max-w-[190px]">Use this angle to test real backend image upload.</p>
                    </div>
                    <span className="text-[11px] font-mono px-2 py-1 bg-slate-100 text-slate-700 rounded border border-slate-200">Drag &amp; drop or click</span>
                  </div>
                )}
                
                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] text-slate-500">{selectedFile ? selectedFile.name : 'Supports JPG, PNG, WebP up to 5MB'}</span>
                  <button className="text-xs text-blue-600 font-semibold hover:underline" type="button">
                    {selectedFile ? 'Change File' : 'Choose File'}
                  </button>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    accept="image/jpeg, image/png, image/webp"
                    onChange={handleFileChange} 
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3.5 rounded-lg bg-slate-50 text-slate-700 border border-slate-200">
              <Icon name="info" className="text-slate-500 text-[20px]" />
              <div className="flex-1">
                <p className="text-xs text-slate-600">Evidence images are automatically matched against statutory physical dimensions via optical scale reference.</p>
              </div>
              <span className="font-mono text-xs text-slate-500 font-medium">ASPECT: 16:9 NATIVE</span>
            </div>
          </div>
        </div>

        {/* Right Column: Metadata */}
        <div className="xl:col-span-5 flex flex-col space-y-6">
          <div className="bg-white p-5 sm:p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Icon name="edit_note" className="text-slate-900 text-[20px]" />
                <h2 className="font-bold text-base text-slate-900">Commodity &amp; Package Details</h2>
              </div>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold border border-slate-200">Configured</span>
            </div>
            
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-800">Inspection Location / Notes</label>
                <div className="flex items-center gap-2">
                  <input 
                    value={locationText}
                    onChange={(e) => setLocationText(e.target.value)}
                    className="w-full h-9 px-3 bg-slate-50 rounded-lg text-slate-900 font-mono text-xs border border-slate-200 focus:bg-white focus:ring-1 focus:ring-slate-900 transition-colors" 
                    type="text" 
                    placeholder="e.g. Mumbai Port Warehouse / Retail Cluster" 
                  />
                </div>
              </div>
          </div>

          <div className="bg-white p-5 sm:p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Icon name="task_alt" className="text-slate-900 text-[20px]" />
                <h3 className="font-bold text-base text-slate-900">Intake Readiness Checklist</h3>
              </div>
              <span className={`font-mono text-xs px-2.5 py-0.5 rounded-full font-semibold border ${selectedFile ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-200'}`}>
                {selectedFile ? '1/1 Ready' : '0/1 Image Required'}
              </span>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2.5">
                  <Icon name={selectedFile ? "check_circle" : "radio_button_unchecked"} className={selectedFile ? "text-emerald-600 text-[18px]" : "text-amber-500 text-[18px]"} />
                  <span className="text-xs font-medium text-slate-800">
                    {selectedFile ? `Package Image Attached (${selectedFile.name})` : 'Attach Front PDP Package Photo'}
                  </span>
                </div>
                <span className={`text-[11px] font-semibold uppercase ${selectedFile ? 'text-emerald-700' : 'text-amber-700'}`}>
                  {selectedFile ? 'Ready' : 'Pending'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2.5">
                  <Icon name="check_circle" className="text-emerald-600 text-[18px]" />
                  <span className="text-xs font-medium text-slate-800">Commodity Context &amp; Barcode Provided</span>
                </div>
                <span className="text-[11px] font-semibold text-emerald-700 uppercase">Provided</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2.5">
                  <Icon name="check_circle" className="text-emerald-600 text-[18px]" />
                  <span className="text-xs font-medium text-slate-800">Standard LM(PC) Statutory Ruleset Calibrated</span>
                </div>
                <span className="text-[11px] font-semibold text-emerald-700 uppercase">Active</span>
              </div>
            </div>
            <div className="p-3 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-xs font-bold text-slate-900">Ready for Compliance Analysis</span>
              </div>
              <span className="font-mono text-xs text-slate-500">Pipeline Latency: ~1.8s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-xl shadow-lg border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 sticky bottom-4 z-30">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button className="h-10 px-4 rounded-lg bg-slate-100 text-slate-400 transition-colors text-xs font-semibold flex items-center justify-center gap-2 border border-slate-200 flex-1 sm:flex-initial cursor-not-allowed opacity-50" type="button" disabled title="Not supported">
            <Icon name="save" className="text-[17px]" /> Save Intake Draft
          </button>
          <button className="h-10 px-4 rounded-lg bg-white text-slate-600 hover:text-rose-600 transition-colors text-xs font-semibold flex items-center justify-center gap-2 border border-slate-200 flex-1 sm:flex-initial" type="button" onClick={() => {
            setSelectedFile(null);
            setFilePreviewUrl(null);
          }}>
            <Icon name="restart_alt" className="text-[17px]" /> Reset Fields
          </button>
        </div>
        <div className="flex items-center gap-4 w-full sm:w-auto justify-end">
          <div className="hidden md:flex flex-col text-right">
            <span className="text-xs font-semibold text-slate-900">Evidence Validation Engine</span>
            <span className="text-xs text-slate-500">Ready for Verification</span>
          </div>
          <button 
            className={`h-10 px-6 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-all text-xs font-semibold flex items-center justify-center gap-2 shadow-sm w-full sm:w-auto ${isSubmitting ? 'opacity-70 cursor-wait' : ''}`}
            type="button"
            onClick={handleStartAnalysis}
            disabled={isSubmitting}
          >
            <span>{isSubmitting ? 'Processing...' : 'Submit & Connect'}</span>
            {!isSubmitting && <Icon name="arrow_forward" className="text-[16px]" />}
          </button>
        </div>
      </div>
      
      {/* Bottom info */}
      <div className="px-2 flex flex-col sm:flex-row items-center justify-between text-slate-400 text-xs gap-2">
        <span className="font-mono">Officer Intake Terminal Session ID: 0x9B42F · Node: S-DELHI-04</span>
        <span>Legal Metrology (Packaged Commodities) Verification Environment</span>
      </div>
    </div>
  );
};

export default NewInspection;
