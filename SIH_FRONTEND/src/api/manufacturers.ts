import { ApiClient } from './client';
import type { 
  ManufacturerListResponse, 
  ManufacturerDetailResponse, 
  ManufacturerHistoryResponse 
} from './types';

export const manufacturersApi = {
  getManufacturers: async (params?: Record<string, any>): Promise<ManufacturerListResponse> => {
    return ApiClient.get<ManufacturerListResponse>('/manufacturers', params);
  },

  getManufacturerById: async (manufacturerId: string): Promise<ManufacturerDetailResponse> => {
    return ApiClient.get<ManufacturerDetailResponse>(`/manufacturers/${manufacturerId}`);
  },

  getManufacturerHistory: async (manufacturerId: string, params?: Record<string, any>): Promise<ManufacturerHistoryResponse> => {
    return ApiClient.get<ManufacturerHistoryResponse>(`/manufacturers/${manufacturerId}/history`, params);
  },
};
