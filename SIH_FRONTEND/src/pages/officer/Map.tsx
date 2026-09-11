import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { inspectionsApi } from '../../api/inspections';
import type { LocationMarker, InspectionListItem } from '../../api/types';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const Map: React.FC = () => {
  const [locations, setLocations] = useState<LocationMarker[]>([]);
  const [recentInspections, setRecentInspections] = useState<InspectionListItem[]>([]);
  const [compliantCount, setCompliantCount] = useState(0);
  const [totalInspections, setTotalInspections] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [locRes, recentRes, compRes, allRes] = await Promise.all([
          inspectionsApi.getLocations({ page: 1, page_size: 100 }),
          inspectionsApi.getInspections({ page: 1, page_size: 3 }),
          inspectionsApi.getInspections({ page: 1, page_size: 1, compliance_status: 'COMPLIANT' }),
          inspectionsApi.getInspections({ page: 1, page_size: 1 })
        ]);
        setLocations(locRes.items || []);
        setRecentInspections(recentRes.items || []);
        setCompliantCount(compRes.pagination.total_items);
        setTotalInspections(allRes.pagination.total_items);
      } catch (err) {
        console.error('Failed to load map data:', err);
      }
    };
    fetchData();
  }, []);

  const nonCompliantCount = totalInspections - compliantCount;
  const complianceRate = totalInspections > 0 ? ((compliantCount / totalInspections) * 100).toFixed(1) : '0.0';

  const validLocations = locations.filter(loc => loc.latitude != null && loc.longitude != null);
  const center: [number, number] = validLocations.length > 0 
    ? [validLocations[0].latitude!, validLocations[0].longitude!] 
    : [18.6276, 73.8131];

  return (
    <div className="flex flex-col w-full space-y-6 pb-8">
      <div className="flex flex-col gap-space-sm pt-space-base pb-space-md">
        <div className="flex flex-wrap items-center justify-between gap-space-sm">
          <div className="flex items-center gap-space-xs font-label-md text-label-md text-on-surface-variant">
            <span className="text-on-surface font-semibold">Officer Portal</span>
            <span className="text-outline">/</span>
            <span className="">Regional Operations</span>
            <span className="text-outline">/</span>
            <span className="text-on-surface font-semibold">Inspection Map</span>
          </div>
        </div>
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-space-base mt-space-xs">
          <div className="space-y-space-2xs">
            <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Geographic Inspection Distribution</h1>
          </div>
          <div className="flex flex-wrap items-center gap-space-sm bg-surface-container-lowest p-space-xs rounded-xl shadow-sm">
            <button disabled className="h-9 px-space-base bg-slate-200 text-slate-400 rounded-lg font-label-md text-label-md flex items-center gap-space-xs cursor-not-allowed" title="Filtering not yet available">
              <Icon name="tune" className="text-[16px]" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-space-base mt-space-sm relative">
        <div className="xl:col-span-8 flex flex-col relative h-[620px] lg:h-[720px] rounded-xl overflow-hidden bg-surface-container shadow-md z-0">
          <MapContainer center={center} zoom={6} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {validLocations.map((loc) => {
              const isError = loc.compliance_status === 'NON_COMPLIANT';
              const isWarning = loc.compliance_status === 'INCONCLUSIVE';
              const color = isError ? 'red' : (isWarning ? 'orange' : 'green');
              
              // Custom div icon
              const markerIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
                iconSize: [16, 16],
                iconAnchor: [8, 8]
              });

              return (
                <Marker key={loc.inspection_id} position={[loc.latitude!, loc.longitude!]} icon={markerIcon}>
                  <Popup>
                    <div className="text-center">
                      <p className="font-bold">{loc.manufacturer || 'Unknown Location'}</p>
                      <p>{loc.compliance_status}</p>
                      <Link to={`/app/inspection/${loc.inspection_id}`} className="text-blue-600 underline text-sm mt-1 inline-block">
                        View Dossier
                      </Link>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
          {validLocations.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-[500] rounded-xl">
              <div className="text-center space-y-2 p-6">
                <Icon name="location_off" className="text-[48px] text-slate-300" />
                <p className="text-sm font-semibold text-slate-600">No Geo-Tagged Inspections</p>
                <p className="text-xs text-slate-400">Inspections with valid latitude/longitude coordinates will appear here.</p>
              </div>
            </div>
          )}
        </div>

        <div className="xl:col-span-4 flex flex-col gap-space-base z-0">
          <div className="bg-surface-container-lowest p-space-base rounded-xl shadow-sm space-y-space-md">
            <div className="grid grid-cols-3 gap-space-xs bg-surface-container-low p-space-sm rounded-lg">
              <div className="flex flex-col">
                <span className="font-code-sm text-code-sm text-on-surface-variant">Inspections</span>
                <span className="font-headline-md text-headline-md text-on-surface font-bold">{totalInspections}</span>
              </div>
              <div className="flex flex-col">
                <span className="font-code-sm text-code-sm text-error">Non-Compliant</span>
                <span className="font-headline-md text-headline-md text-error font-bold">{nonCompliantCount}</span>
              </div>
              <div className="flex flex-col">
                <span className="font-code-sm text-code-sm text-on-surface-variant">Rate</span>
                <span className="font-headline-md text-headline-md text-on-surface font-bold">{complianceRate}%</span>
              </div>
            </div>
          </div>
          
          <div className="bg-surface-container-lowest p-space-base rounded-xl shadow-sm flex flex-col flex-1">
            <div className="flex items-center justify-between pb-space-sm">
              <span className="font-headline-sm text-headline-sm text-on-surface font-bold">Audit Records at Node</span>
              <span className="font-code-sm text-code-sm text-on-surface-variant">Showing latest 3</span>
            </div>
            <div className="space-y-space-sm flex-1 overflow-y-auto">
              {recentInspections.map((item) => (
                <div key={item.id} className="bg-surface-container-low p-space-sm rounded-lg space-y-space-xs hover:bg-surface-container transition-colors">
                  <div className="flex items-center justify-between">
                    <span className="font-code-sm text-code-sm font-semibold text-on-surface">{item.inspection_code}</span>
                    <span className="text-xs font-bold">{item.compliance_status || 'PENDING'}</span>
                  </div>
                  <div>
                    <p className="font-headline-sm text-headline-sm text-on-surface font-semibold truncate">{item.product_name_ai || 'Unknown Product'}</p>
                  </div>
                  <div className="flex items-center justify-between pt-space-xs">
                    <span className="font-code-sm text-code-sm text-on-surface-variant">{item.inspection_date ? new Date(item.inspection_date).toLocaleDateString() : ''}</span>
                    <Link className="px-space-sm py-space-2xs rounded bg-surface-container-highest text-on-surface font-label-sm text-label-sm hover:bg-outline-variant transition-colors flex items-center gap-space-2xs" to={`/app/inspection/${item.id}`}>
                      <span className="">View Dossier</span>
                      <Icon name="chevron_right" className="text-[14px]" />
                    </Link>
                  </div>
                </div>
              ))}
              {recentInspections.length === 0 && (
                <div className="text-center text-on-surface-variant py-8">No records available</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Map;
