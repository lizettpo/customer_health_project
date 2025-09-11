import React from 'react';
import { formatDate, formatScore } from '../../utils/formatters';
import { getHealthScoreColor } from '../../utils/healthScore';


const HistoricalChart = ({ scores }) => {
  if (!scores || scores.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Historical Scores</h3>
        <p className="text-gray-500">No historical data available</p>
      </div>
    );
  }

  const maxScore = 100;
  const minScore = 0;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Historical Scores</h3>
      
      <div className="space-y-4">
        {scores.slice(0, 10).map((score, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1">
              <div className="text-sm text-gray-600 w-32">
                {formatDate(score.calculated_at)}
              </div>
              
              <div className="flex-1 relative">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full transition-all duration-300"
                    style={{
                      width: `${score.score}%`,
                      backgroundColor: getHealthScoreColor(score.score),
                    }}
                  />
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span
                  className="text-lg font-bold"
                  style={{ color: getHealthScoreColor(score.score) }}
                >
                  {formatScore(score.score)}
                </span>
                <span
                  className="text-xs px-2 py-1 rounded-full font-medium"
                  style={{
                    backgroundColor: getHealthScoreColor(score.score) + '20',
                    color: getHealthScoreColor(score.score),
                  }}
                >
                  {score.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {scores.length > 10 && (
        <div className="mt-4 text-center">
          <span className="text-sm text-gray-500">
            Showing latest 10 of {scores.length} records
          </span>
        </div>
      )}
    </div>
  );
};

export default HistoricalChart;