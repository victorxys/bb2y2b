import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { downloadsApi } from '../lib/downloadsApi';

export function useActiveTasks(refetchInterval?: number) {
  return useQuery({
    queryKey: ['downloads', 'active'],
    queryFn: downloadsApi.getActiveTasks,
    refetchInterval: refetchInterval || 2000, // 默认2秒刷新一次
  });
}

export function useAllTasks(refetchInterval?: number | false) {
  return useQuery({
    queryKey: ['downloads', 'all'],
    queryFn: downloadsApi.getAllTasks,
    refetchInterval: refetchInterval === false ? false : (refetchInterval || 2000), // 默认2秒刷新
  });
}

export function useDownloadedFiles() {
  return useQuery({
    queryKey: ['downloads', 'files'],
    queryFn: downloadsApi.getDownloadedFiles,
  });
}

export function useRemoveTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: downloadsApi.removeTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['downloads'] });
    },
  });
}

export function useClearCompletedTasks() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: downloadsApi.clearCompletedTasks,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['downloads'] });
    },
  });
}

export function useDeleteFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: downloadsApi.deleteFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['downloads', 'files'] });
    },
  });
}
