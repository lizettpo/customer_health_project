export const getHealthScoreColor = (score) => {
  if (score >= 75) return '#10B981'; // Green
  if (score >= 60) return '#F59E0B'; // Yellow/Orange
  return '#EF4444'; // Red
};

export const getHealthStatusColor = (status) => {
  switch (status) {
    case 'healthy':
      return '#10B981'; // Green
    case 'at_risk':
      return '#F59E0B'; // Yellow/Orange
    case 'critical':
      return '#EF4444'; // Red
    default:
      return '#6B7280'; // Gray
  }
};

export const formatHealthStatus = (status) => {
  switch (status) {
    case 'healthy':
      return 'Healthy';
    case 'at_risk':
      return 'At Risk';
    case 'critical':
      return 'Critical';
    default:
      return 'Unknown';
  }
};

export const calculateTrendDirection = (currentScore, previousScore) => {
  const difference = currentScore - previousScore;
  if (Math.abs(difference) < 2) return 'stable';
  return difference > 0 ? 'up' : 'down';
};