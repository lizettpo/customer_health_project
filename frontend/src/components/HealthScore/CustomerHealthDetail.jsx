import React, { useState } from "react";
import { useHealthScore } from "../../hooks";
import HealthFactorCard from "./HealthFactorCard";
import CustomerActivityForm from "./CustomerActivityForm";
import { formatDate, formatScore, formatNumber } from "../../utils/formatters";
import {
  getHealthScoreColor,
  formatHealthStatus,
} from "../../utils/healthScore";
import "./CustomerHealthDetail.css";

const CustomerHealthDetail = ({ customerId }) => {
  const [showActivityForm, setShowActivityForm] = useState(false);
  const { healthScore, loading, error, refetch, calculateScore } =
    useHealthScore(customerId);

  const handleEventRecorded = (eventData) => {
    setShowActivityForm(false);
    // Refetch health score to get updated data
    setTimeout(() => {
      refetch();
    }, 1000); // Small delay to allow backend processing
  };

  if (loading) {
    return (
      <div className="health-detail-loading">
        <div className="loading-summary-card">
          <div className="loading-title"></div>
          <div className="loading-content"></div>
        </div>
        <div className="loading-factors-grid">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="loading-factor-card">
              <div className="loading-factor-title"></div>
              <div className="loading-factor-content"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="health-detail-error">
        <div className="error-content">
          <div className="error-info">
            <h3>Error Loading Health Score</h3>
            <p>{error}</p>
          </div>
          <button onClick={refetch} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!healthScore) {
    return (
      <div className="no-data-card">
        <p className="no-data-text">
          No health score data available for this customer.
        </p>
      </div>
    );
  }

  const factorIcons = {
    api_usage: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
    ),
    login_frequency: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    ),
    payment_timeliness: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
        />
      </svg>
    ),
    feature_adoption: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
        />
      </svg>
    ),
    support_tickets: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  };

  const getHealthStatusClass = (score) => {
    if (score >= 80) return "healthy";
    if (score >= 60) return "at-risk";
    return "critical";
  };

  return (
    <div className="customer-health-detail">
      {/* Overall Health Score Summary */}
      <div className="health-summary-card">
        <div className="health-summary-header">
          <div className="customer-info">
            <h2>{healthScore.customer_name}</h2>
            <p>Last calculated: {formatDate(healthScore.calculated_at)}</p>
          </div>

          <div className="health-score-display">
            <div
              className={`overall-score overall-score--${getHealthStatusClass(
                healthScore.overall_score
              )}`}
            >
              {formatScore(healthScore.overall_score)}
            </div>
            <div
              className={`health-status-badge health-status-badge--${getHealthStatusClass(
                healthScore.overall_score
              )}`}
            >
              {formatHealthStatus(healthScore.status)}
            </div>
          </div>
        </div>

        <div className="health-summary-footer">
          <div className="customer-segment">
            Customer Segment:{" "}
            <span>{healthScore.data_summary.customer_segment}</span>
          </div>
          <button
            onClick={() => setShowActivityForm(true)}
            className="record-activity-btn"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Record Activity
          </button>
        </div>
      </div>

      {/* Activity Recording Form */}
      {showActivityForm && (
        <CustomerActivityForm
          customerId={customerId}
          onEventRecorded={handleEventRecorded}
          onClose={() => setShowActivityForm(false)}
        />
      )}
      {/* Health Factors */}
      <div className="health-factors-section">
        <h3>Health Factors</h3>
        <div className="health-factors-grid">
          {Object.entries(healthScore.factors).map(([key, factor]) => (
            <HealthFactorCard
              key={key}
              title={key
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase())}
              factor={factor}
              icon={factorIcons[key]}
            />
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {healthScore.recommendations.length > 0 && (
        <div className="recommendations-card">
          <h3 className="recommendations-title">Recommendations</h3>
          <ul className="recommendations-list">
            {healthScore.recommendations.map((recommendation, index) => (
              <li key={index} className="recommendation-item">
                <svg
                  className="recommendation-icon"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="recommendation-text">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CustomerHealthDetail;
