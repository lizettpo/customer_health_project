import React, { useState } from "react";
import { useCustomers } from "../../hooks";
import { formatDate, formatScore } from "../../utils/formatters";
import {
  getHealthStatusColor,
  formatHealthStatus,
} from "../../utils/healthScore";
import "./CustomersList.css";

const CustomersList = ({ onCustomerSelect }) => {
  const [healthStatusFilter, setHealthStatusFilter] = useState("all");
  const [page, setPage] = useState(0);
  const limit = 10;

  const { customers, loading, error, refetch } = useCustomers({
    health_status:
      healthStatusFilter === "all" ? undefined : healthStatusFilter,
  });

  if (loading) {
    return (
      <div className="customers-list-loading">
        <div className="customers-list-header">
          <h3 className="customers-list-title">Customers</h3>
        </div>
        <div className="customers-list-skeleton">
          <div className="skeleton-space">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton-item"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="customers-list-error">
        <div className="customers-list-error-text">Error loading customers: {error}</div>
      </div>
    );
  }

  return (
    <div className="customers-list">
      <div className="customers-list-header">
        <div className="customers-list-header-content">
          <h3 className="customers-list-title">Customers</h3>

          <div className="customers-list-filters">
            <select
              value={healthStatusFilter}
              onChange={(e) => {
                setHealthStatusFilter(e.target.value);
                setPage(0);
              }}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value="all">All Customers</option>
              <option value="healthy">Healthy</option>
              <option value="at_risk">At Risk</option>
              <option value="critical">Critical</option>
            </select>
            
            <button
              onClick={refetch}
              className="flex items-center px-3 py-1 text-sm bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
              disabled={loading}
            >
              <svg className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {customers.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No customers found
          </div>
        ) : (
          customers.map((customer) => (
            <div
              key={customer.id}
              className={`p-6 hover:bg-gray-50 transition-colors ${
                onCustomerSelect ? "cursor-pointer" : ""
              }`}
              onClick={() => onCustomerSelect?.(customer)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="text-lg font-medium text-gray-900 mb-1">
                    {customer.name}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">{customer.email}</p>
                  <p className="text-xs text-gray-500">
                    Created: {formatDate(customer.created_at)}
                  </p>
                </div>

                <div className="text-right">
                  {customer.health_score !== undefined ? (
                    <>
                      <div className={`health-score health-score--${customer.health_status || "critical"}`}>
                        {formatScore(customer.health_score)}
                      </div>
                      <div className={`health-status-badge health-status-badge--${customer.health_status || "critical"}`}>
                        {formatHealthStatus(customer.health_status || "critical")}
                      </div>
                    </>
                  ) : (
                    <div className="text-sm text-gray-400">No score</div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {customers.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <span className="text-sm text-gray-600">Page {page + 1}</span>

          <button
            onClick={() => setPage(page + 1)}
            disabled={customers.length < limit}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default CustomersList;
