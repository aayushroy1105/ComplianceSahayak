import { ApiClient } from './client';
import type { AnalyticsRepeatOffendersResponse } from './types';

export const analyticsApi = {
  getRepeatOffenders: async (): Promise<AnalyticsRepeatOffendersResponse> => {
    return ApiClient.get<AnalyticsRepeatOffendersResponse>('/analytics/repeat-offenders');
  },
};
