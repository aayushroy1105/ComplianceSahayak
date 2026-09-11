import { ApiClient } from './client';
import type { ReportResponse } from './types';

export const reportsApi = {
  generateReport: async (inspectionId: string): Promise<void> => {
    return ApiClient.post<void>(`/inspections/${inspectionId}/report`);
  },

  getReport: async (inspectionId: string): Promise<ReportResponse> => {
    return ApiClient.get<ReportResponse>(`/inspections/${inspectionId}/report`);
  },
};
