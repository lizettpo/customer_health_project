import React from "react";
import { useDashboardStats } from "../../hooks";
import {
  formatNumber,
  formatPercentage,
  formatDate,
} from "../../utils/formatters";
import { getHealthStatusColor } from "../../utils/healthScore";
import "./DashboardStats.css";

const DashboardStats = () => {
  const { stats, loading, error, refetch } = useDashboardStats();

  if (loading) {
    return (
      <div className="dashboard-stats-loading">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="stat-card-skeleton">
            <div className="skeleton-title"></div>
            <div className="skeleton-value"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-stats-error">
        <p className="dashboard-stats-error-text">Error loading dashboard stats: {error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    {
      title: "Total Customers",
      value: formatNumber(stats.total_customers),
      cssClass: "total",
    },
    {
      title: "Healthy",
      value: `${formatNumber(stats.healthy_customers)} (${formatPercentage(
        stats.distribution.healthy_percent
      )})`,
      cssClass: "healthy",
    },
    {
      title: "At Risk",
      value: `${formatNumber(stats.at_risk_customers)} (${formatPercentage(
        stats.distribution.at_risk_percent
      )})`,
      cssClass: "at-risk",
    },
    {
      title: "Critical",
      value: `${formatNumber(stats.critical_customers)} (${formatPercentage(
        stats.distribution.critical_percent
      )})`,
      cssClass: "critical",
    },
  ];

  return (
    <div className="dashboard-stats">
      <div className="dashboard-stats-grid">
        {statCards.map((card, index) => (
          <div key={index} className="stat-card">
            <div className={`stat-card-title stat-card-title--${card.cssClass}`}>
              {card.title}
            </div>
            <div className={`stat-card-value stat-card-value--${card.cssClass}`}>
              {card.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DashboardStats;
