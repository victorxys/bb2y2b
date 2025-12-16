import { api } from './api';

export interface Video {
  id: number;
  bvid: string;
  aid?: string;
  title: string;
  description?: string;
  bilibili_url?: string;
  cover_url?: string;
  video_type?: string;
  space_id?: number;
  status: string;
  start_p?: number;
  end_p?: number;
  duration?: string;
  download_path?: string;
  cover_path?: string;
  subtitle_path?: string;
  created_at: string;
  updated_at: string;
}

export const videosApi = {
  getVideos: async (params?: { status?: string; video_type?: string }): Promise<Video[]> => {
    const response = await api.get('/videos/', { params });
    return response.data;
  },

  deleteVideo: async (bvid: string): Promise<void> => {
    await api.delete(`/videos/${bvid}`);
  },

  startDownload: async (bvid: string): Promise<{ message: string; task_id: string }> => {
    const response = await api.post(`/videos/${bvid}/download`);
    return response.data;
  },
};