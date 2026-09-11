import { ApiClient } from './client';
import type { 
  InspectionCreateRequest, 
  InspectionCreateResponse, 
  InspectionDetailResponse,
  InspectionImageResponse,
  InspectionListResponse,
  LocationMarkersResponse
} from './types';

export const inspectionsApi = {
  createInspection: async (data: InspectionCreateRequest): Promise<InspectionCreateResponse> => {
    return ApiClient.post<InspectionCreateResponse>('/inspections', data);
  },

  uploadImage: async (inspectionId: string, imageFile: File, imageType: string = 'FRONT'): Promise<InspectionImageResponse> => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('image_type', imageType);

    return ApiClient.post<InspectionImageResponse>(`/inspections/${inspectionId}/images`, formData);
  },

  analyze: async (inspectionId: string): Promise<InspectionDetailResponse> => {
    return ApiClient.post<InspectionDetailResponse>(`/inspections/${inspectionId}/analyze`);
  },

  getInspection: async (inspectionId: string): Promise<InspectionDetailResponse> => {
    return ApiClient.get<InspectionDetailResponse>(`/inspections/${inspectionId}`);
  },

  updateReviewStatus: async (inspectionId: string, status: string): Promise<InspectionDetailResponse> => {
    return ApiClient.patch<InspectionDetailResponse>(`/inspections/${inspectionId}/review-status`, { status });
  },

  getInspections: async (params?: Record<string, any>): Promise<InspectionListResponse> => {
    return ApiClient.get<InspectionListResponse>('/inspections', params);
  },

  getLocations: async (params?: Record<string, any>): Promise<LocationMarkersResponse> => {
    return ApiClient.get<LocationMarkersResponse>('/inspections/locations', params);
  },

  issueNotice: async (inspectionId: string, remarks?: string): Promise<any> => {
    return ApiClient.post<any>(`/inspections/${inspectionId}/notice`, { remarks });
  },

  shareReport: async (inspectionId: string): Promise<{share_url: string, expires_at: string}> => {
    return ApiClient.post<{share_url: string, expires_at: string}>(`/inspections/${inspectionId}/report/share`);
  },

  getNotices: async (inspectionId: string): Promise<any[]> => {
    return ApiClient.get<any[]>(`/inspections/${inspectionId}/notices`);
  },
};
