import React from 'react';
import { formatScore } from '../../utils/formatters';
import { getHealthScoreColor } from '../../utils/healthScore';
import './HealthFactorCard.css';


const HealthFactorCard = ({ title, factor, icon }) => {
  const getHealthStatusClass = (score) => {
    if (score >= 80) return "healthy";
    if (score >= 60) return "at-risk";
    return "critical";
  };

  return (
    <div className="health-factor-card">
      <div className="factor-header">
        <div className="factor-title-section">
          {icon && (
            <div className="factor-icon">
              {icon}
            </div>
          )}
          <h3 className="factor-title">{title}</h3>
        </div>
        <div className={`factor-score factor-score--${getHealthStatusClass(factor.score)}`}>
          {formatScore(factor.score)}
        </div>
      </div>

      <div className="factor-content">
        <div className="factor-value-section">
          <div className="factor-label">Current Value</div>
          <div className="factor-value">
            {factor.value.toLocaleString()}
          </div>
        </div>

        <div className="factor-assessment-section">
          <div className="factor-label">Assessment</div>
          <div className="factor-description">
            {factor.description}
          </div>
        </div>

        <div className="factor-progress-section">
          <div className="factor-progress-track">
            <div
              className={`factor-progress-fill factor-progress-fill--${getHealthStatusClass(factor.score)}`}
              style={{ width: `${factor.score}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthFactorCard;