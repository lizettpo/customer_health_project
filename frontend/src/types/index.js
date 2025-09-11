// Type definitions for reference - since we're using JavaScript, these are just comments

/*
Customer: {
  id: number,
  name: string,
  email: string,
  created_at: string,
  health_score?: number,
  health_status?: 'healthy' | 'at_risk' | 'critical'
}

HealthFactor: {
  score: number,
  value: number,
  description: string
}

HealthScoreDetail: {
  customer_id: number,
  customer_name: string,
  overall_score: number,
  status: 'healthy' | 'at_risk' | 'critical',
  factors: {
    api_usage: HealthFactor,
    login_frequency: HealthFactor,
    payment_timeliness: HealthFactor,
    feature_adoption: HealthFactor,
    support_tickets: HealthFactor
  },
  calculated_at: string,
  historical_scores: HistoricalScore[],
  recommendations: string[],
  data_summary: {
    events_analyzed: number,
    history_points: number,
    customer_segment: string
  }
}

HistoricalScore: {
  score: number,
  status: 'healthy' | 'at_risk' | 'critical',
  calculated_at: string
}

DashboardStats: {
  total_customers: number,
  healthy_customers: number,
  at_risk_customers: number,
  critical_customers: number,
  average_health_score: number,
  health_coverage_percentage: number,
  distribution: {
    healthy_percent: number,
    at_risk_percent: number,
    critical_percent: number
  },
  last_updated: string
}
*/