import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import CustomerHealthDetail from './components/HealthScore/CustomerHealthDetail';
import './App.css';

const App = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route 
            path="/customer/:customerId" 
            element={<CustomerHealthDetailWrapper />} 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

// Wrapper component to handle the customerId parameter
const CustomerHealthDetailWrapper = () => {
  const params = new URLSearchParams(window.location.search);
  const pathSegments = window.location.pathname.split('/');
  const customerId = parseInt(pathSegments[pathSegments.length - 1]);

  if (isNaN(customerId)) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <a
            href="/"
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            <svg 
              className="w-5 h-5 mr-2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </a>
        </div>
        <CustomerHealthDetail customerId={customerId} />
      </div>
    </div>
  );
};

export default App;