import React, { useState } from 'react';
import { useCustomers } from '../../hooks';
import { formatDate, formatScore } from '../../utils/formatters';
import { getHealthStatusColor, formatHealthStatus } from '../../utils/healthScore';
import { Customer } from '../../types';

interface CustomersListProps {
  onCustomerSelect?: (customer: Customer) => void;
}

const CustomersList: React.FC<CustomersListProps> = ({ onCustomerSelect }) => {
  const [healthStatusFilter, setHealthStatusFilter] = useState<'all' | 'healthy' | 'at_risk' | 'critical'>('all');
  const [page, setPage] = useState(0);
  const limit = 10;

  const { customers, loading, error } = useCustomers({
    limit,
    offset: page * limit,
    health_status: healthStatusFilter === 'all' ? undefined : healthStatusFilter,
  });

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Customers</h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600">Error loading customers: {error}</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Customers</h3>
          
          <select
            value={healthStatusFilter}
            onChange={(e) => {
              setHealthStatusFilter(e.target.value as any);
              setPage(0);
            }}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm"
          >
            <option value="all">All Customers</option>
            <option value="healthy">Healthy</option>
            <option value="at_risk">At Risk</option>
            <option value="critical">Critical</option>
          </select>
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
                onCustomerSelect ? 'cursor-pointer' : ''
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
                      <div
                        className="text-2xl font-bold mb-1"
                        style={{ color: getHealthStatusColor(customer.health_status || 'critical') }}
                      >
                        {formatScore(customer.health_score)}
                      </div>
                      <div
                        className="text-sm font-medium px-2 py-1 rounded-full"
                        style={{
                          backgroundColor: getHealthStatusColor(customer.health_status || 'critical') + '20',
                          color: getHealthStatusColor(customer.health_status || 'critical'),
                        }}
                      >
                        {formatHealthStatus(customer.health_status || 'critical')}
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
          
          <span className="text-sm text-gray-600">
            Page {page + 1}
          </span>
          
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