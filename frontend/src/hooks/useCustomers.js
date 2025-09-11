import { useState, useEffect } from "react";
import { CustomerService } from "../services/customerService";

export const useCustomers = (params) => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await CustomerService.getCustomers(params);
      setCustomers(data.data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch customers"
      );
      console.error("Error in useCustomers:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [params?.limit, params?.offset, params?.health_status]);

  const refetch = () => {
    fetchCustomers();
  };

  return {
    customers,
    loading,
    error,
    refetch,
  };
};
