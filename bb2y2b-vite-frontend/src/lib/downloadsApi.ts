import { api } from './api';

export interface DownloadTask {
  task_id: string;
  bvid: string;
  title: string;
  status: 'pending' | 'downloading' | 'merging' | 'completed' | 'error' | 'cancelled';
  current_page: number;
  total_pages: number;
  current_bytes: number;
  total_bytes: number;
  speed: number;
  speed_formatted: string;
  eta: number;
  eta_formatted: string;
  progress_percent: number;
  stage: string;
  stage_message: string;
  merge_progress: number;
  total_duration: number;
  total_duration_formatted: string;
  started_at: string | null;
  completed_at: string | null;
  download_path: string | null;
  cover_path: string | null;
  error_message: string | null;
}

export interface DownloadedFile {
  name: string;
  path: string;
  size: number;
  size_formatted: string;
  created_at: number;
  type: string;
  bvid: string | null;
  title: string | null;
  cover_path: string | null;
  cover_url: string | null;
  subtitle_path: string | null;
  has_subtitle: boolean;
}

export interface SubtitleContent {
  filename: string;
  content: string;
  size: number;
}

export const downloadsApi = {
  // 任务管理
  getAllTasks: async (): Promise<{ tasks: DownloadTask[]; total: number }> => {
    const response = await api.get('/downloads/tasks');
    return response.data;
  },

  getActiveTasks: async (): Promise<{ tasks: DownloadTask[]; total: number }> => {
    const response = await api.get('/downloads/tasks/active');
    return response.data;
  },

  getTask: async (taskId: string): Promise<DownloadTask> => {
    const response = await api.get(`/downloads/tasks/${taskId}`);
    return response.data;
  },

  getTaskByBvid: async (bvid: string): Promise<DownloadTask> => {
    const response = await api.get(`/downloads/tasks/bvid/${bvid}`);
    return response.data;
  },

  removeTask: async (taskId: string): Promise<void> => {
    await api.delete(`/downloads/tasks/${taskId}`);
  },

  clearCompletedTasks: async (): Promise<void> => {
    await api.post('/downloads/tasks/clear-completed');
  },

  // 文件管理
  getDownloadedFiles: async (): Promise<{ files: DownloadedFile[]; total: number }> => {
    const response = await api.get('/downloads/files');
    return response.data;
  },

  deleteFile: async (filename: string): Promise<void> => {
    await api.delete(`/downloads/file/${filename}`);
  },

  getFileUrl: (filename: string): string => {
    return `${api.defaults.baseURL}/downloads/file/${filename}`;
  },

  getCoverUrl: (filename: string): string => {
    return `${api.defaults.baseURL}/downloads/cover/${filename}`;
  },

  getStreamUrl: (filename: string): string => {
    return `${api.defaults.baseURL}/downloads/stream/${filename}`;
  },

  // 字幕管理
  getSubtitle: async (filename: string): Promise<SubtitleContent> => {
    const response = await api.get(`/downloads/subtitle/${filename}`);
    return response.data;
  },

  getSubtitleDownloadUrl: (filename: string): string => {
    return `${api.defaults.baseURL}/downloads/subtitle/download/${filename}`;
  },
};
