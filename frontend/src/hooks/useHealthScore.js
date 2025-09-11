import { useState, useEffect } from 'react';
import { HealthScoreService } from '../services/healthScoreService';

export const useHealthScore = (customerId) => {
  const [healthScore, setHealthScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealthScore = async () => {
    if (!customerId) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await HealthScoreService.getCustomerHealthDetail(customerId);
      setHealthScore(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health score');
      console.error('Error in useHealthScore:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthScore();
  }, [customerId]);

  const refetch = () => {
    fetchHealthScore();
  };

  const calculateScore = async () => {
    try {
      setError(null);
      await HealthScoreService.calculateHealthScore(customerId);
      // Refresh the health score data
      await fetchHealthScore();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate health score');
      console.error('Error calculating health score:', err);
    }
  };

  return {
    healthScore,
    loading,
    error,
    refetch,
    calculateScore,
  };
};