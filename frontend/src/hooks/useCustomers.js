import { useState, useEffect } from "react";
import { CustomerService } from "../services/customerService";

export const useCustomers = (params) => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentParams, setCurrentParams] = useState(params);

  const fetchCustomers = async (paramsToUse = currentParams) => {
    try {
      setLoading(true);
      setError(null);
      const data = await CustomerService.getCustomers(paramsToUse);
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
    setCurrentParams(params);
    fetchCustomers(params);
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
