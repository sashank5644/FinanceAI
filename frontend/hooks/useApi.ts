import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { AgentRequest, AgentResponse } from '@/types';

// Agent hooks
export const useExecuteAgent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: AgentRequest) => apiClient.executeAgent(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-history'] });
    },
  });
};

export const useAvailableAgents = () => {
  return useQuery({
    queryKey: ['available-agents'],
    queryFn: () => apiClient.getAvailableAgents(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Research hooks
export const useResearchHistory = (limit = 10, offset = 0) => {
  return useQuery({
    queryKey: ['research-history', limit, offset],
    queryFn: () => apiClient.getResearchHistory(limit, offset),
  });
};

// Knowledge Graph hooks
export const useGraphStats = () => {
  return useQuery({
    queryKey: ['graph-stats'],
    queryFn: () => apiClient.getGraphStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.checkHealth(),
    refetchInterval: 10000, // Check every 10 seconds
  });
};
