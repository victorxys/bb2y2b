import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { videosApi } from '../lib/videosApi';

export const VIDEOS_QUERY_KEY = ['videos'];

export const useVideos = (params?: { status?: string; video_type?: string }) => {
  return useQuery({
    queryKey: [...VIDEOS_QUERY_KEY, params],
    queryFn: () => videosApi.getVideos(params),
  });
};

export const useDeleteVideo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (bvid: string) => videosApi.deleteVideo(bvid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOS_QUERY_KEY });
    },
  });
};

export const useStartDownload = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (bvid: string) => videosApi.startDownload(bvid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOS_QUERY_KEY });
    },
  });
};