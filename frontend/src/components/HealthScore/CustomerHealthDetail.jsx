import React, { useState } from "react";
import { useHealthScore } from "../../hooks";
import HealthFactorCard from "./HealthFactorCard";
import HistoricalChart from "./HistoricalChart";
import CustomerActivityForm from "./CustomerActivityForm";
import { formatDate, formatScore, formatNumber } from "../../utils/formatters";
import {
  getHealthScoreColor,
  formatHealthStatus,
} from "../../utils/healthScore";

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
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-lg shadow p-6 animate-pulse"
            >
              <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-16 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-red-800">
              Error Loading Health Score
            </h3>
            <p className="text-red-600 mt-1">{error}</p>
          </div>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!healthScore) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">
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

  return (
    <div className="space-y-6">
      {/* Overall Health Score Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {healthScore.customer_name}
            </h2>
            <p className="text-gray-600">
              Last calculated: {formatDate(healthScore.calculated_at)}
            </p>
          </div>

          <div className="text-right">
            <div
              className="text-4xl font-bold mb-2"
              style={{ color: getHealthScoreColor(healthScore.overall_score) }}
            >
              {formatScore(healthScore.overall_score)}
            </div>
            <div
              className="inline-block px-3 py-1 rounded-full text-sm font-medium"
              style={{
                backgroundColor:
                  getHealthScoreColor(healthScore.overall_score) + "20",
                color: getHealthScoreColor(healthScore.overall_score),
              }}
            >
              {formatHealthStatus(healthScore.status)}
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Customer Segment:{" "}
            <span className="font-medium">
              {healthScore.data_summary.customer_segment}
            </span>
          </div>
          <button
            onClick={() => setShowActivityForm(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
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

      {/* Data Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Data Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-600">Events Analyzed</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(healthScore.data_summary.events_analyzed)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">History Points</div>
            <div className="text-2xl font-bold text-green-600">
              {formatNumber(healthScore.data_summary.history_points)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Customer Segment</div>
            <div className="text-2xl font-bold text-purple-600">
              {healthScore.data_summary.customer_segment}
            </div>
          </div>
        </div>
      </div>

      {/* Health Factors */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Health Factors
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recommendations
          </h3>
          <ul className="space-y-2">
            {healthScore.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start">
                <svg
                  className="w-5 h-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Historical Data */}
      <HistoricalChart scores={healthScore.historical_scores} />
    </div>
  );
};

export default CustomerHealthDetail;
