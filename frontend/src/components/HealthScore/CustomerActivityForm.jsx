import React, { useState } from "react";
import { CustomerService } from "../../services/customerService";
import "./CustomerActivityForm.css";

const CustomerActivityForm = ({ customerId, onEventRecorded, onClose }) => {
  const [eventType, setEventType] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form fields for different event types - corrected to match backend
  const [apiCallData, setApiCallData] = useState({
    endpoint: "",
    method: "GET",
    response_code: "200",
    response_time_ms: "",
  });

  const [paymentData, setPaymentData] = useState({
    amount: "",
    status: "paid_on_time",
    payment_method: "credit_card",
    invoice_number: "",
  });

  const [loginData, setLoginData] = useState({
    ip_address: "",
    user_agent: "",
    login_method: "password",
  });

  const [featureUsageData, setFeatureUsageData] = useState({
    feature_name: "",
    usage_duration_minutes: "",
  });

  const [supportTicketData, setSupportTicketData] = useState({
    priority: "medium",
    ticket_type: "technical_issue",
    status: "open",
  });

  const predefinedEventTypes = [
    {
      value: "login",
      label: "User Login",
      description: "Record a user login event",
    },
    {
      value: "api_call",
      label: "API Call",
      description: "Record an API usage event",
    },
    {
      value: "payment",
      label: "Payment",
      description: "Record a payment-related event",
    },
    {
      value: "feature_use",
      label: "Feature Usage",
      description: "Record feature adoption/usage",
    },
    {
      value: "support_ticket",
      label: "Support Ticket",
      description: "Record a support interaction",
    },
  ];


  const isFormValid = () => {
    if (!eventType) return false;

    switch (eventType) {
      case "api_call":
        return apiCallData.endpoint.trim() !== "";
      case "payment":
        return paymentData.amount && parseFloat(paymentData.amount) > 0;
      case "feature_use":
        return featureUsageData.feature_name !== "";
      case "login":
        return loginData.ip_address.trim() !== "";
      case "support_ticket":
        return true; // All fields have default values
      default:
        return true;
    }
  };

  const getEventData = () => {
    switch (eventType) {
      case "login":
        return {
          ip_address: loginData.ip_address || undefined,
          user_agent: loginData.user_agent || undefined,
          login_method: loginData.login_method,
        };
      case "api_call":
        return {
          endpoint: apiCallData.endpoint || undefined,
          method: apiCallData.method,
          response_code: apiCallData.response_code
            ? parseInt(apiCallData.response_code)
            : undefined,
          response_time_ms: apiCallData.response_time_ms
            ? parseInt(apiCallData.response_time_ms)
            : undefined,
        };
      case "payment":
        return {
          amount: paymentData.amount
            ? parseFloat(paymentData.amount)
            : undefined,
          status: paymentData.status,
          payment_method: paymentData.payment_method,
          invoice_number: paymentData.invoice_number || undefined,
        };
      case "feature_use":
        return {
          feature_name: featureUsageData.feature_name || undefined,
          usage_duration_minutes: featureUsageData.usage_duration_minutes
            ? parseInt(featureUsageData.usage_duration_minutes)
            : undefined,
        };
      case "support_ticket":
        return {
          priority: supportTicketData.priority,
          ticket_type: supportTicketData.ticket_type,
          status: supportTicketData.status,
        };
      default:
        return {};
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const eventData = getEventData();

      // Remove undefined values from eventData
      const cleanEventData = eventData
        ? Object.fromEntries(
            Object.entries(eventData).filter(
              ([_, value]) => value !== undefined
            )
          )
        : null;

      const result = await CustomerService.recordCustomerEvent(customerId, {
        event_type: eventType,
        event_data:
          Object.keys(cleanEventData || {}).length > 0 ? cleanEventData : null,
      });

      if (result.success) {
        // Reset form
        setEventType("");
        setApiCallData({
          endpoint: "",
          method: "GET",
          response_code: "200",
          response_time_ms: "",
        });
        setLoginData({
          ip_address: "",
          user_agent: "",
          login_method: "password",
        });
        setPaymentData({
          amount: "",
          status: "paid_on_time",
          payment_method: "credit_card",
          invoice_number: "",
        });
        setFeatureUsageData({
          feature_name: "",
          usage_duration_minutes: "",
        });
        setSupportTicketData({
          priority: "medium",
          ticket_type: "technical_issue",
          status: "open",
        });

        // Notify parent component
        if (onEventRecorded) {
          onEventRecorded(result.data);
        }
      } else {
        throw new Error(result.detail || "Failed to record event");
      }
    } catch (error) {
      console.error("Error recording event:", error);
      alert(`Failed to record event: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedEventType = predefinedEventTypes.find(
    (type) => type.value === eventType
  );

  const renderApiCallFields = () => (
    <div className="form-fields">
      <div className="grid-container">
        <div className="field-group">
          <label className="form-label">
            API Endpoint *
          </label>
          <input
            type="text"
            value={apiCallData.endpoint}
            onChange={(e) =>
              setApiCallData({ ...apiCallData, endpoint: e.target.value })
            }
            placeholder="/api/customers/data"
            className="form-input"
            required
          />
        </div>
        <div className="field-group">
          <label className="form-label">
            HTTP Method
          </label>
          <select
            value={apiCallData.method}
            onChange={(e) =>
              setApiCallData({ ...apiCallData, method: e.target.value })
            }
            className="form-select"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
      </div>
      <div className="field-group">
        <label className="form-label">
          Response Code
        </label>
        <select
          value={apiCallData.response_code}
          onChange={(e) =>
            setApiCallData({ ...apiCallData, response_code: e.target.value })
          }
          className="form-select"
        >
          <option value="200">200 - Success</option>
          <option value="201">201 - Created</option>
          <option value="400">400 - Bad Request</option>
          <option value="401">401 - Unauthorized</option>
          <option value="404">404 - Not Found</option>
          <option value="500">500 - Server Error</option>
        </select>
      </div>
      <div className="field-group">
        <label className="form-label">
          Response Time (ms)
        </label>
        <input
          type="number"
          value={apiCallData.response_time_ms}
          onChange={(e) =>
            setApiCallData({ ...apiCallData, response_time_ms: e.target.value })
          }
          placeholder="250"
          className="form-input"
        />
      </div>
    </div>
  );

  const renderLoginFields = () => (
    <div className="form-fields">
      <div className="grid-container">
        <div className="field-group">
          <label className="form-label">
            IP Address *
          </label>
          <input
            type="text"
            value={loginData.ip_address}
            onChange={(e) =>
              setLoginData({ ...loginData, ip_address: e.target.value })
            }
            placeholder="192.168.1.1"
            className="form-input"
          />
        </div>
        <div className="field-group">
          <label className="form-label">
            Login Method
          </label>
          <select
            value={loginData.login_method}
            onChange={(e) =>
              setLoginData({ ...loginData, login_method: e.target.value })
            }
            className="form-select"
          >
            <option value="password">Password</option>
            <option value="sso">Single Sign-On</option>
            <option value="api_key">API Key</option>
            <option value="oauth">OAuth</option>
          </select>
        </div>
      </div>
      <div className="field-group">
        <label className="form-label">
          User Agent
        </label>
        <input
          type="text"
          value={loginData.user_agent}
          onChange={(e) =>
            setLoginData({ ...loginData, user_agent: e.target.value })
          }
          placeholder="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          className="form-input"
        />
      </div>
    </div>
  );

  const renderPaymentFields = () => (
    <div className="form-fields">
      <div className="grid-container">
        <div className="field-group">
          <label className="form-label">
            Amount *
          </label>
          <input
            type="number"
            step="0.01"
            value={paymentData.amount}
            onChange={(e) =>
              setPaymentData({ ...paymentData, amount: e.target.value })
            }
            placeholder="299.99"
            className="form-input"
            required
          />
        </div>
        <div className="field-group">
          <label className="form-label">
            Payment Status *
          </label>
          <select
            value={paymentData.status}
            onChange={(e) =>
              setPaymentData({ ...paymentData, status: e.target.value })
            }
            className="form-input"
            required
          >
            <option value="paid_on_time">Paid On Time</option>
            <option value="paid_late">Paid Late</option>
            <option value="overdue">Overdue</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>
      <div className="field-group">
        <label className="form-label">
          Payment Method
        </label>
        <select
          value={paymentData.payment_method}
          onChange={(e) =>
            setPaymentData({ ...paymentData, payment_method: e.target.value })
          }
          className="form-input"
        >
          <option value="credit_card">Credit Card</option>
          <option value="bank_transfer">Bank Transfer</option>
          <option value="check">Check</option>
          <option value="invoice">Invoice</option>
          <option value="paypal">PayPal</option>
        </select>
      </div>
      <div className="field-group">
        <label className="form-label">
          Invoice Number
        </label>
        <input
          type="text"
          value={paymentData.invoice_number}
          onChange={(e) =>
            setPaymentData({ ...paymentData, invoice_number: e.target.value })
          }
          placeholder="INV-2024-001"
          className="form-input"
        />
      </div>
    </div>
  );

  const renderFeatureUsageFields = () => (
    <div className="form-fields">
      <div className="field-group">
        <label className="form-label">
          Feature Name *
        </label>
        <select
          value={featureUsageData.feature_name}
          onChange={(e) =>
            setFeatureUsageData({
              ...featureUsageData,
              feature_name: e.target.value,
            })
          }
          className="form-input"
          required
        >
          <option value="">Select a feature</option>
          <option value="dashboard">Dashboard</option>
          <option value="reports">Reports</option>
          <option value="analytics">Analytics</option>
          <option value="notifications">Notifications</option>
          <option value="integrations">Integrations</option>
          <option value="workflows">Workflows</option>
          <option value="templates">Templates</option>
          <option value="exports">Exports</option>
        </select>
      </div>
      <div className="field-group">
        <label className="form-label">
          Usage Duration (minutes)
        </label>
        <input
          type="number"
          value={featureUsageData.usage_duration_minutes}
          onChange={(e) =>
            setFeatureUsageData({
              ...featureUsageData,
              usage_duration_minutes: e.target.value,
            })
          }
          placeholder="15"
          className="form-input"
        />
      </div>
    </div>
  );

  const renderSupportTicketFields = () => (
    <div className="form-fields">
      <div className="grid-container">
        <div className="field-group">
          <label className="form-label">
            Priority *
          </label>
          <select
            value={supportTicketData.priority}
            onChange={(e) =>
              setSupportTicketData({
                ...supportTicketData,
                priority: e.target.value,
              })
            }
            className="form-select"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div className="field-group">
          <label className="form-label">
            Ticket Type *
          </label>
          <select
            value={supportTicketData.ticket_type}
            onChange={(e) =>
              setSupportTicketData({
                ...supportTicketData,
                ticket_type: e.target.value,
              })
            }
            className="form-input"
            required
          >
            <option value="technical_issue">Technical Issue</option>
            <option value="billing_question">Billing Question</option>
            <option value="feature_request">Feature Request</option>
            <option value="account_issue">Account Issue</option>
            <option value="integration_help">Integration Help</option>
            <option value="general_inquiry">General Inquiry</option>
          </select>
        </div>
      </div>
      <div className="field-group">
        <label className="form-label">
          Ticket Status *
        </label>
        <select
          value={supportTicketData.status}
          onChange={(e) =>
            setSupportTicketData({
              ...supportTicketData,
              status: e.target.value,
            })
          }
          className="form-input"
          required
        >
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
      </div>
    </div>
  );


  return (
    <div className="activity-form-container">
        <div className="form-header">
          <h3 className="form-title">
            Record Customer Activity
          </h3>
          {onClose && (
            <button
              onClick={onClose}
              className="close-button"
            >
              <svg
                className="close-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="form">
          {/* Event Type Selection */}
          <div className="event-type-section">
            <label className="form-label">
              Event Type *
            </label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="event-type-select"
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
              <p className="event-description">
                {selectedEventType.description}
              </p>
            )}
          </div>

          {/* Event Data Fields */}
          {eventType && (
            <div className="event-details-section">
              <label className="event-details-label">
                Event Details
              </label>
              {eventType === "login" && renderLoginFields()}
              {eventType === "api_call" && renderApiCallFields()}
              {eventType === "payment" && renderPaymentFields()}
              {eventType === "feature_use" && renderFeatureUsageFields()}
              {eventType === "support_ticket" && renderSupportTicketFields()}
            </div>
          )}

          {/* Submit Button */}
          <div className="submit-section">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="cancel-button"
                disabled={isSubmitting}
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={isSubmitting || !isFormValid()}
              className={`submit-button ${isFormValid() && !isSubmitting ? 'enabled' : ''}`}
            >
              {isSubmitting ? "Recording..." : "Record Event"}
            </button>
          </div>
        </form>
      </div>
  );
};

export default CustomerActivityForm;