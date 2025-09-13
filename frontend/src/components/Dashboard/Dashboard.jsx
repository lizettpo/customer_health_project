import React, { useState } from "react";
import DashboardStats from "./DashboardStats";
import CustomersList from "./CustomersList";
import CustomerHealthDetail from "../HealthScore/CustomerHealthDetail";

const Dashboard = () => {
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
  };

  const handleBackToList = () => {
    setSelectedCustomer(null);
    // Force refresh of dashboard data when returning from detail view
    setRefreshKey((prev) => prev + 1);
  };

  if (selectedCustomer) {
    return (
      <div className="min-h-screen bg-gray-100">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <button
              onClick={handleBackToList}
              className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Dashboard
            </button>
          </div>
          <CustomerHealthDetail customerId={selectedCustomer.id} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Customer Health Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Monitor customer health scores and track engagement metrics
          </p>
        </div>

        <DashboardStats key={`stats-${refreshKey}`} />
        <CustomersList
          key={`customers-${refreshKey}`}
          onCustomerSelect={handleCustomerSelect}
        />
      </div>
    </div>
  );
};

export default Dashboard;
