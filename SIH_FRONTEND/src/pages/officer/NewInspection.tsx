import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { ApiError } from '../../api/types';

type AngleType = 'FRONT' | 'BACK' | 'SIDE' | 'OTHER';
interface UploadedAngle {
  file: File;
  previewUrl: string;
  type: AngleType;
  id: string;
}

const NewInspection: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const pendingAngleRef = useRef<AngleType>('FRONT');
  const [angles, setAngles] = useState<UploadedAngle[]>([]);
  const [uploadedAngleIds, setUploadedAngleIds] = useState<Set<string>>(new Set());
  
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [locationText, setLocationText] = useState('retail');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude);
          setLongitude(position.coords.longitude);
        },
        (error) => {
          console.warn("Geolocation access denied or unavailable:", error);
        }
      );
    }
  }, []);

  const initiateUpload = (type: AngleType) => {
    pendingAngleRef.current = type;
    fileInputRef.current?.click();
  };

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
    const newAngle: UploadedAngle = {
      file,
      previewUrl: URL.createObjectURL(file),
      type: pendingAngleRef.current,
      id: Math.random().toString(36).substring(7)
    };
    
    setAngles(prev => [...prev, newAngle]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleStartAnalysis = async () => {
    if (angles.length === 0) {
      setErrorMsg('Please select at least one package image file before submitting intake.');
      return;
    }

    setIsSubmitting(true);
    let currentInspectionId = '';

    try {
      // 1. Create Inspection
      const createRes = await inspectionsApi.createInspection({
        location_text: locationText || 'Delhi NCR Field Zone',
        inspection_date: new Date().toISOString(),
        ...(latitude !== null && longitude !== null ? { latitude, longitude } : {})
      });
      currentInspectionId = createRes.id;

      // 2. Upload Images
      for (const angle of angles) {
        if (!uploadedAngleIds.has(angle.id)) {
          await inspectionsApi.uploadImage(currentInspectionId, angle.file, angle.type);
          setUploadedAngleIds(prev => new Set(prev).add(angle.id));
        }
      }

      // 3. Trigger Real AI Analysis Pipeline
      await inspectionsApi.analyze(currentInspectionId);

      // Success, go to Dossier
      navigate(`/app/inspection/${currentInspectionId}`);
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

            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="image/jpeg, image/png, image/webp"
              onChange={handleFileChange} 
            />
            
            {angles.length === 0 ? (
              <div className="group relative w-full rounded-xl bg-slate-50 border-2 border-dashed border-slate-200 p-6 sm:p-8 flex flex-col items-center justify-center text-center shadow-inner">
                <div className="w-14 h-14 rounded-full bg-white shadow-sm border border-slate-100 flex items-center justify-center text-slate-500 mb-3">
                  <Icon name="add_a_photo" className="text-[30px]" />
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
            ) : (
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
              </div>
            )}

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
              <span className={`font-mono text-xs px-2.5 py-0.5 rounded-full font-semibold border ${angles.length > 0 ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-200'}`}>
                {angles.length > 0 ? `${angles.length} Angle(s) Ready` : '0 Images Uploaded'}
              </span>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2.5">
                  <Icon name={angles.length > 0 ? "check_circle" : "radio_button_unchecked"} className={angles.length > 0 ? "text-emerald-600 text-[18px]" : "text-amber-500 text-[18px]"} />
                  <span className="text-xs font-medium text-slate-800">
                    {angles.length > 0 ? `${angles.length} Package Images Attached` : 'Attach Front PDP Package Photo'}
                  </span>
                </div>
                <span className={`text-[11px] font-semibold uppercase ${angles.length > 0 ? 'text-emerald-700' : 'text-amber-700'}`}>
                  {angles.length > 0 ? 'Ready' : 'Pending'}
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
            angles.forEach(a => URL.revokeObjectURL(a.previewUrl));
            setAngles([]);
            setUploadedAngleIds(new Set());
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
            className={`h-10 px-6 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-all text-xs font-semibold flex items-center justify-center gap-2 shadow-sm w-full sm:w-auto ${isSubmitting || angles.length === 0 ? 'opacity-70 cursor-wait' : ''}`}
            type="button"
            onClick={handleStartAnalysis}
            disabled={isSubmitting || angles.length === 0}
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
