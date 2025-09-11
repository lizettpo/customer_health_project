import React, { useState } from 'react';
import { CustomerService } from '../../services/customerService';

const CustomerActivityForm = ({ customerId, onEventRecorded, onClose }) => {
  const [eventType, setEventType] = useState('');
  const [customEventType, setCustomEventType] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form fields for different event types
  const [apiCallData, setApiCallData] = useState({
    endpoint: '',
    method: 'GET',
    response_time: '',
    status_code: '200'
  });
  
  const [loginData, setLoginData] = useState({
    user_id: '',
    session_duration: '',
    login_method: 'password',
    ip_address: ''
  });
  
  const [paymentData, setPaymentData] = useState({
    amount: '',
    currency: 'USD',
    status: 'completed',
    method: 'credit_card',
    invoice_id: ''
  });
  
  const [featureUsageData, setFeatureUsageData] = useState({
    feature: '',
    usage_duration: '',
    actions_performed: '',
    reports_generated: ''
  });
  
  const [supportTicketData, setSupportTicketData] = useState({
    ticket_id: '',
    priority: 'medium',
    category: '',
    resolved: true,
    resolution_time: ''
  });

  const predefinedEventTypes = [
    { value: 'api_call', label: 'API Call', description: 'Record an API usage event' },
    { value: 'login', label: 'User Login', description: 'Record a user login event' },
    { value: 'payment', label: 'Payment', description: 'Record a payment-related event' },
    { value: 'feature_usage', label: 'Feature Usage', description: 'Record feature adoption/usage' },
    { value: 'support_ticket', label: 'Support Ticket', description: 'Record a support interaction' },
    { value: 'custom', label: 'Custom Event', description: 'Record a custom event type' }
  ];

  const getEventData = () => {
    switch (eventType) {
      case 'api_call':
        return {
          endpoint: apiCallData.endpoint || undefined,
          method: apiCallData.method,
          response_time: apiCallData.response_time ? parseInt(apiCallData.response_time) : undefined,
          status_code: apiCallData.status_code ? parseInt(apiCallData.status_code) : undefined
        };
      case 'login':
        return {
          user_id: loginData.user_id || undefined,
          session_duration: loginData.session_duration ? parseInt(loginData.session_duration) : undefined,
          login_method: loginData.login_method,
          ip_address: loginData.ip_address || undefined
        };
      case 'payment':
        return {
          amount: paymentData.amount ? parseFloat(paymentData.amount) : undefined,
          currency: paymentData.currency,
          status: paymentData.status,
          method: paymentData.method,
          invoice_id: paymentData.invoice_id || undefined
        };
      case 'feature_usage':
        return {
          feature: featureUsageData.feature || undefined,
          usage_duration: featureUsageData.usage_duration ? parseInt(featureUsageData.usage_duration) : undefined,
          actions_performed: featureUsageData.actions_performed ? parseInt(featureUsageData.actions_performed) : undefined,
          reports_generated: featureUsageData.reports_generated ? parseInt(featureUsageData.reports_generated) : undefined
        };
      case 'support_ticket':
        return {
          ticket_id: supportTicketData.ticket_id || undefined,
          priority: supportTicketData.priority,
          category: supportTicketData.category || undefined,
          resolved: supportTicketData.resolved,
          resolution_time: supportTicketData.resolution_time ? parseInt(supportTicketData.resolution_time) : undefined
        };
      default:
        return {};
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const finalEventType = eventType === 'custom' ? customEventType : eventType;
      const eventData = getEventData();
      
      // Remove undefined values from eventData
      const cleanEventData = Object.fromEntries(
        Object.entries(eventData).filter(([_, value]) => value !== undefined)
      );

      const result = await CustomerService.recordCustomerEvent(customerId, {
        event_type: finalEventType,
        event_data: Object.keys(cleanEventData).length > 0 ? cleanEventData : null,
        timestamp: new Date().toISOString()
      });
      
      if (result.success) {
        // Reset form
        setEventType('');
        setCustomEventType('');
        setApiCallData({ endpoint: '', method: 'GET', response_time: '', status_code: '200' });
        setLoginData({ user_id: '', session_duration: '', login_method: 'password', ip_address: '' });
        setPaymentData({ amount: '', currency: 'USD', status: 'completed', method: 'credit_card', invoice_id: '' });
        setFeatureUsageData({ feature: '', usage_duration: '', actions_performed: '', reports_generated: '' });
        setSupportTicketData({ ticket_id: '', priority: 'medium', category: '', resolved: true, resolution_time: '' });
        
        // Notify parent component
        if (onEventRecorded) {
          onEventRecorded(result.data);
        }
        
        alert('Event recorded successfully! Health score will be recalculated in the background.');
      } else {
        throw new Error(result.detail || 'Failed to record event');
      }
    } catch (error) {
      console.error('Error recording event:', error);
      alert(`Failed to record event: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedEventType = predefinedEventTypes.find(type => type.value === eventType);

  const renderApiCallFields = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">API Endpoint</label>
          <input
            type="text"
            value={apiCallData.endpoint}
            onChange={(e) => setApiCallData({...apiCallData, endpoint: e.target.value})}
            placeholder="/api/customers/data"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">HTTP Method</label>
          <select
            value={apiCallData.method}
            onChange={(e) => setApiCallData({...apiCallData, method: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Response Time (ms)</label>
          <input
            type="number"
            value={apiCallData.response_time}
            onChange={(e) => setApiCallData({...apiCallData, response_time: e.target.value})}
            placeholder="150"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status Code</label>
          <input
            type="number"
            value={apiCallData.status_code}
            onChange={(e) => setApiCallData({...apiCallData, status_code: e.target.value})}
            placeholder="200"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderLoginFields = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">User ID/Email</label>
          <input
            type="text"
            value={loginData.user_id}
            onChange={(e) => setLoginData({...loginData, user_id: e.target.value})}
            placeholder="john.smith@company.com"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Session Duration (seconds)</label>
          <input
            type="number"
            value={loginData.session_duration}
            onChange={(e) => setLoginData({...loginData, session_duration: e.target.value})}
            placeholder="3600"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Login Method</label>
          <select
            value={loginData.login_method}
            onChange={(e) => setLoginData({...loginData, login_method: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="password">Password</option>
            <option value="sso">SSO</option>
            <option value="oauth">OAuth</option>
            <option value="api_key">API Key</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">IP Address</label>
          <input
            type="text"
            value={loginData.ip_address}
            onChange={(e) => setLoginData({...loginData, ip_address: e.target.value})}
            placeholder="192.168.1.100"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderPaymentFields = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
          <input
            type="number"
            step="0.01"
            value={paymentData.amount}
            onChange={(e) => setPaymentData({...paymentData, amount: e.target.value})}
            placeholder="299.99"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
          <select
            value={paymentData.currency}
            onChange={(e) => setPaymentData({...paymentData, currency: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="CAD">CAD</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            value={paymentData.status}
            onChange={(e) => setPaymentData({...paymentData, status: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
          <select
            value={paymentData.method}
            onChange={(e) => setPaymentData({...paymentData, method: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="credit_card">Credit Card</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="paypal">PayPal</option>
            <option value="stripe">Stripe</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Invoice ID</label>
          <input
            type="text"
            value={paymentData.invoice_id}
            onChange={(e) => setPaymentData({...paymentData, invoice_id: e.target.value})}
            placeholder="INV-2024-001"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderFeatureUsageFields = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Feature Name</label>
        <input
          type="text"
          value={featureUsageData.feature}
          onChange={(e) => setFeatureUsageData({...featureUsageData, feature: e.target.value})}
          placeholder="analytics_dashboard"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Usage Duration (seconds)</label>
          <input
            type="number"
            value={featureUsageData.usage_duration}
            onChange={(e) => setFeatureUsageData({...featureUsageData, usage_duration: e.target.value})}
            placeholder="1800"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Actions Performed</label>
          <input
            type="number"
            value={featureUsageData.actions_performed}
            onChange={(e) => setFeatureUsageData({...featureUsageData, actions_performed: e.target.value})}
            placeholder="15"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Reports Generated</label>
          <input
            type="number"
            value={featureUsageData.reports_generated}
            onChange={(e) => setFeatureUsageData({...featureUsageData, reports_generated: e.target.value})}
            placeholder="3"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderSupportTicketFields = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ticket ID</label>
          <input
            type="text"
            value={supportTicketData.ticket_id}
            onChange={(e) => setSupportTicketData({...supportTicketData, ticket_id: e.target.value})}
            placeholder="SUP-2024-456"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            value={supportTicketData.priority}
            onChange={(e) => setSupportTicketData({...supportTicketData, priority: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <input
            type="text"
            value={supportTicketData.category}
            onChange={(e) => setSupportTicketData({...supportTicketData, category: e.target.value})}
            placeholder="technical_issue"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Resolution Time (minutes)</label>
          <input
            type="number"
            value={supportTicketData.resolution_time}
            onChange={(e) => setSupportTicketData({...supportTicketData, resolution_time: e.target.value})}
            placeholder="240"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={supportTicketData.resolved}
            onChange={(e) => setSupportTicketData({...supportTicketData, resolved: e.target.checked})}
            className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span className="text-sm font-medium text-gray-700">Ticket Resolved</span>
        </label>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Record Customer Activity
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Event Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Event Type *
          </label>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select an event type</option>
            {predefinedEventTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {selectedEventType && (
            <p className="mt-1 text-sm text-gray-600">
              {selectedEventType.description}
            </p>
          )}
        </div>

        {/* Custom Event Type Input */}
        {eventType === 'custom' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Event Type *
            </label>
            <input
              type="text"
              value={customEventType}
              onChange={(e) => setCustomEventType(e.target.value)}
              placeholder="e.g., product_demo, trial_started, etc."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
        )}

        {/* Event Data Fields */}
        {eventType && eventType !== 'custom' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Event Details
            </label>
            {eventType === 'api_call' && renderApiCallFields()}
            {eventType === 'login' && renderLoginFields()}
            {eventType === 'payment' && renderPaymentFields()}
            {eventType === 'feature_usage' && renderFeatureUsageFields()}
            {eventType === 'support_ticket' && renderSupportTicketFields()}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isSubmitting || !eventType || (eventType === 'custom' && !customEventType)}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? 'Recording...' : 'Record Event'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CustomerActivityForm;