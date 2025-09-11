import React from 'react';
import { HealthFactor } from '../../types';
import { formatScore } from '../../utils/formatters';
import { getHealthScoreColor } from '../../utils/healthScore';

interface HealthFactorCardProps {
  title: string;
  factor: HealthFactor;
  icon?: React.ReactNode;
}

const HealthFactorCard: React.FC<HealthFactorCardProps> = ({ title, factor, icon }) => {
  const scoreColor = getHealthScoreColor(factor.score);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          {icon && (
            <div className="mr-3 text-gray-500">
              {icon}
            </div>
          )}
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        <div 
          className="text-2xl font-bold"
          style={{ color: scoreColor }}
        >
          {formatScore(factor.score)}
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-sm text-gray-600 mb-1">Current Value</div>
          <div className="text-lg font-medium text-gray-900">
            {factor.value.toLocaleString()}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-600 mb-1">Assessment</div>
          <div className="text-sm text-gray-700">
            {factor.description}
          </div>
        </div>

        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-300"
              style={{
                width: `${factor.score}%`,
                backgroundColor: scoreColor,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthFactorCard;