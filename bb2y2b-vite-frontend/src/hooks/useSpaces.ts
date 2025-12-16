import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { spacesApi } from '../lib/api';
import type { SpaceCreate, SpaceUpdate } from '../lib/api';

// Query keys
export const QUERY_KEYS = {
  spaces: ['spaces'] as const,
  space: (id: string) => ['spaces', id] as const,
};

// Get all spaces
export const useSpaces = () => {
  return useQuery({
    queryKey: QUERY_KEYS.spaces,
    queryFn: spacesApi.getSpaces,
  });
};

// Get single space
export const useSpace = (spaceId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.space(spaceId),
    queryFn: () => spacesApi.getSpace(spaceId),
    enabled: !!spaceId,
  });
};

// Create space mutation
export const useCreateSpace = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: SpaceCreate) => spacesApi.createSpace(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.spaces });
    },
  });
};

// Update space mutation
export const useUpdateSpace = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ spaceId, data }: { spaceId: string; data: SpaceUpdate }) =>
      spacesApi.updateSpace(spaceId, data),
    onSuccess: (_, { spaceId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.spaces });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.space(spaceId) });
    },
  });
};

// Delete space mutation
export const useDeleteSpace = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (spaceId: string) => spacesApi.deleteSpace(spaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.spaces });
    },
  });
};

// Scan space mutation
export const useScanSpace = () => {
  return useMutation({
    mutationFn: (spaceId: string) => spacesApi.scanSpace(spaceId),
  });
};