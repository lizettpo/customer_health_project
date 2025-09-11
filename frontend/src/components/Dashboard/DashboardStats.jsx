import React from 'react';
import { useDashboardStats } from '../../hooks';
import { formatNumber, formatPercentage, formatDate } from '../../utils/formatters';
import { getHealthStatusColor } from '../../utils/healthScore';

const DashboardStats: React.FC = () => {
  const { stats, loading, error } = useDashboardStats();

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
        <p className="text-red-600">Error loading dashboard stats: {error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    {
      title: 'Total Customers',
      value: formatNumber(stats.total_customers),
      color: '#3B82F6',
    },
    {
      title: 'Healthy',
      value: `${formatNumber(stats.healthy_customers)} (${formatPercentage(stats.distribution.healthy_percent)})`,
      color: getHealthStatusColor('healthy'),
    },
    {
      title: 'At Risk',
      value: `${formatNumber(stats.at_risk_customers)} (${formatPercentage(stats.distribution.at_risk_percent)})`,
      color: getHealthStatusColor('at_risk'),
    },
    {
      title: 'Critical',
      value: `${formatNumber(stats.critical_customers)} (${formatPercentage(stats.distribution.critical_percent)})`,
      color: getHealthStatusColor('critical'),
    },
  ];

  return (
    <div className="mb-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div 
              className="text-sm font-medium text-gray-600 mb-2"
              style={{ borderLeft: `4px solid ${card.color}`, paddingLeft: '8px' }}
            >
              {card.title}
            </div>
            <div className="text-2xl font-bold" style={{ color: card.color }}>
              {card.value}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Overview</h3>
          <span className="text-sm text-gray-500">
            Last updated: {formatDate(stats.last_updated)}
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-600 mb-1">Average Health Score</div>
            <div className="text-3xl font-bold text-blue-600">
              {stats.average_health_score.toFixed(1)}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-600 mb-1">Health Coverage</div>
            <div className="text-3xl font-bold text-green-600">
              {formatPercentage(stats.health_coverage_percentage)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardStats;