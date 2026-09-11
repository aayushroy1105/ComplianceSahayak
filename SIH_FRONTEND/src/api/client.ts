const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiClient {
  private static getHeaders(customHeaders?: HeadersInit): HeadersInit {
    const headers: HeadersInit = {
      ...customHeaders,
    };
    
    // Only set Content-Type if it's not FormData (which sets its own boundary)
    if (!customHeaders || !('Content-Type' in customHeaders)) {
      (headers as Record<string, string>)['Content-Type'] = 'application/json';
    }

    // Extract CSRF token from cookies
    const match = document.cookie.match(new RegExp('(^| )csrf_token=([^;]+)'));
    if (match) {
      (headers as Record<string, string>)['X-CSRF-Token'] = match[2];
    }

    return headers;
  }

  private static async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorDetail = 'Unknown Error';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorDetail = response.statusText;
      }
      throw new Error(errorDetail);
    }
    
    // Some endpoints might return empty body (e.g. 204 No Content)
    if (response.status === 204) {
      return {} as T;
    }
    
    return response.json();
  }

  static async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    let url = `${BASE_URL}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }
    const response = await fetch(url, {
      method: 'GET',
      headers: ApiClient.getHeaders(),
      credentials: 'include',
    });
    return this.handleResponse<T>(response);
  }

  private static async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    customHeaders?: HeadersInit
  ): Promise<T> {
    const isFormData = data instanceof FormData;
    const isUrlEncoded = customHeaders && (customHeaders as Record<string, string>)['Content-Type'] === 'application/x-www-form-urlencoded';
    
    let body: BodyInit | undefined;
    if (isFormData || isUrlEncoded) {
      body = data as BodyInit;
    } else if (data) {
      body = JSON.stringify(data);
    }

    const headers = this.getHeaders(customHeaders);
    if (isFormData) {
      // Remove Content-Type so browser sets it with boundary for FormData
      delete (headers as Record<string, string>)['Content-Type'];
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method,
      headers,
      body,
      credentials: 'include',
    });
    return this.handleResponse<T>(response);
  }

  static async post<T>(endpoint: string, data?: unknown, customHeaders?: HeadersInit): Promise<T> {
    return this.request<T>('POST', endpoint, data, customHeaders);
  }

  static async put<T>(endpoint: string, data?: unknown, customHeaders?: HeadersInit): Promise<T> {
    return this.request<T>('PUT', endpoint, data, customHeaders);
  }

  static async patch<T>(endpoint: string, data?: unknown, customHeaders?: HeadersInit): Promise<T> {
    return this.request<T>('PATCH', endpoint, data, customHeaders);
  }

  static async delete<T>(endpoint: string, data?: unknown, customHeaders?: HeadersInit): Promise<T> {
    return this.request<T>('DELETE', endpoint, data, customHeaders);
  }
}
