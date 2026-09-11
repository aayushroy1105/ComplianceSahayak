import { ApiClient } from './client';
import type { Token, UserResponse } from './types';

export const authApi = {
  login: async (username: string, password: string): Promise<Token> => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    return ApiClient.post<Token>('/auth/login', params, {
      'Content-Type': 'application/x-www-form-urlencoded',
    });
  },

  getMe: async (): Promise<UserResponse> => {
    return ApiClient.get<UserResponse>('/users/me');
  },

  logout: async (): Promise<void> => {
    return ApiClient.post<void>('/auth/logout');
  },

  checkHealth: async (): Promise<{ status: string; database: string; ai_service: string }> => {
    return ApiClient.get('/health');
  },
};
