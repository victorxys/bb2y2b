import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Space types
export interface Space {
  id: number;
  space_id: string;
  space_name: string;
  video_keyword?: string;
  video_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_scan_time?: string;
}

export interface SpaceCreate {
  space_id: string;
  space_name: string;
  video_keyword?: string;
  video_type: string;
  is_active?: boolean;
}

export interface SpaceUpdate {
  space_name?: string;
  video_keyword?: string;
  video_type?: string;
  is_active?: boolean;
}

// API functions
export const spacesApi = {
  // Get all spaces
  getSpaces: async (): Promise<Space[]> => {
    const response = await api.get('/spaces/');
    return response.data;
  },

  // Get space by ID
  getSpace: async (spaceId: string): Promise<Space> => {
    const response = await api.get(`/spaces/${spaceId}`);
    return response.data;
  },

  // Create new space
  createSpace: async (data: SpaceCreate): Promise<Space> => {
    const response = await api.post('/spaces/', data);
    return response.data;
  },

  // Update space
  updateSpace: async (spaceId: string, data: SpaceUpdate): Promise<Space> => {
    const response = await api.put(`/spaces/${spaceId}`, data);
    return response.data;
  },

  // Delete space
  deleteSpace: async (spaceId: string): Promise<void> => {
    await api.delete(`/spaces/${spaceId}`);
  },

  // Scan space
  scanSpace: async (spaceId: string): Promise<{ 
    message: string; 
    task_id: string;
    total_found?: number;
    new_videos?: number;
    updated_videos?: number;
  }> => {
    const response = await api.post(`/spaces/${spaceId}/scan`);
    return response.data;
  },
};