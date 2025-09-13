import api from './api';

export class HealthScoreService {
  static async getCustomerHealthDetail(customerId) {
    try {
      const response = await api.get(`/api/customers/${customerId}/health`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching health detail for customer ${customerId}:`, error);
      throw error;
    }
  }

  static async calculateHealthScore(customerId) {
    try {
      const response = await api.post(`/api/customers/${customerId}/health/calculate`);
      return response.data;
    } catch (error) {
      console.error(`Error calculating health score for customer ${customerId}:`, error);
      throw error;
    }
  }

  static async getDashboardStats() {
    try {
      const response = await api.get('/api/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }
}