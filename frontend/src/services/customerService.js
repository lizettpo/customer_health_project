import api from "./api";

export class CustomerService {
  static async getCustomers(params) {
    try {
      const response = await api.get("/api/customers", { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching customers:", error);
      throw error;
    }
  }

  static async getCustomerById(customerId) {
    try {
      const response = await api.get(`/api/customers/${customerId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching customer ${customerId}:`, error);
      throw error;
    }
  }

  static async recordCustomerEvent(customerId, eventData) {
    try {
      const response = await api.post(
        `/api/customers/${customerId}/events`,
        eventData
      );
      return response.data;
    } catch (error) {
      console.error(`Error recording event for customer ${customerId}:`, error);
      throw error;
    }
  }

  static async getCustomerEvents(customerId, days = 90) {
    try {
      const response = await api.get(`/api/customers/${customerId}/events`, {
        params: { days },
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching events for customer ${customerId}:`, error);
      throw error;
    }
  }
}
