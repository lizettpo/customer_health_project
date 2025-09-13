# Customer Health Score Guide

## Overview

The Customer Health Score is a comprehensive metric (0-100) that measures customer engagement, satisfaction, and likelihood of retention. It provides actionable insights to help identify at-risk customers and optimize customer success strategies.

## Health Score Categories

The health score is classified into three main categories based on the overall score:

### 🟢 Healthy (80-100)
- **Status**: Customer is highly engaged and satisfied
- **Risk Level**: Low churn risk
- **Action**: Focus on expansion opportunities and maintaining satisfaction
- **Characteristics**: Regular usage, timely payments, high feature adoption

### 🟡 At Risk (60-79)
- **Status**: Customer showing warning signs of disengagement
- **Risk Level**: Medium churn risk  
- **Action**: Proactive outreach, identify pain points, provide additional support
- **Characteristics**: Declining usage, delayed payments, or limited feature adoption

### 🔴 Critical (0-59)
- **Status**: Customer at high risk of churning
- **Risk Level**: High churn risk
- **Action**: Immediate intervention required, emergency customer success review
- **Characteristics**: Poor usage patterns, payment issues, limited engagement

## Health Score Factors

The overall health score is calculated using five weighted factors:

### 1. API Usage (Weight: 25%)

**What it measures**: Frequency and consistency of API calls compared to customer segment expectations.

**Segment Expectations**:
- **Enterprise**: 1000+ API calls expected
- **SMB**: 500+ API calls expected  
- **Startup**: 200+ API calls expected

**What reduces the score**:
- ❌ API usage below segment expectations
- ❌ Declining API call trends over time
- ❌ Long periods of API inactivity
- ❌ Frequent API errors or failures

**What improves the score**:
- ✅ Consistent API usage meeting or exceeding expectations
- ✅ Growing API usage trends
- ✅ Regular, predictable usage patterns
- ✅ Successful API responses with low error rates

### 2. Login Frequency (Weight: 20%)

**What it measures**: How often users from the customer organization log into the platform.

**What reduces the score**:
- ❌ Infrequent logins (less than weekly)
- ❌ Declining login trends
- ❌ Single user dependency (only one person logging in)
- ❌ Long periods without any logins

**What improves the score**:
- ✅ Regular daily/weekly logins
- ✅ Multiple users from the organization logging in
- ✅ Consistent login patterns
- ✅ Increasing user adoption within the organization

### 3. Payment Timeliness (Weight: 20%)

**What it measures**: Customer's payment history and financial reliability.

**What reduces the score**:
- ❌ Late payments (beyond due date)
- ❌ Failed payment attempts
- ❌ Downgrading to lower-tier plans
- ❌ Payment disputes or chargebacks
- ❌ Outstanding overdue invoices

**What improves the score**:
- ✅ Payments made on time or early
- ✅ Automatic payment methods set up
- ✅ Upgrading to higher-tier plans
- ✅ Clean payment history with no issues
- ✅ Annual payment commitments

### 4. Feature Adoption (Weight: 20%)

**What it measures**: Breadth and depth of platform feature usage.

**What reduces the score**:
- ❌ Using only basic features
- ❌ Not exploring new features
- ❌ Abandoning previously used features
- ❌ Low integration with other tools

**What improves the score**:
- ✅ Using advanced features
- ✅ Adopting new features quickly after release
- ✅ Deep integration with existing workflows
- ✅ Utilizing multiple product modules
- ✅ Customizing features for specific use cases

### 5. Support Tickets (Weight: 15%)

**What it measures**: Support interaction patterns and issue resolution success.

**What reduces the score**:
- ❌ High volume of support tickets
- ❌ Recurring issues with the same problems
- ❌ Escalated or unresolved tickets
- ❌ Negative feedback in support interactions
- ❌ Requesting account cancellation or downgrades

**What improves the score**:
- ✅ Few or no support tickets needed
- ✅ Quick resolution of any issues raised
- ✅ Positive feedback and satisfaction ratings
- ✅ Proactive feature requests and suggestions
- ✅ Self-service usage (using documentation/knowledge base)

## Score Calculation

The overall health score is calculated as a weighted average:

```
Health Score = (API Usage × 0.25) + (Login Frequency × 0.20) + 
               (Payment Timeliness × 0.20) + (Feature Adoption × 0.20) + 
               (Support Tickets × 0.15)
```

Each factor is scored individually (0-100) and then combined using the weights above.

## Data Requirements

For accurate health scoring, the system analyzes:

- **API Logs**: Call frequency, success rates, error patterns
- **Login Records**: User authentication logs, session data
- **Billing Data**: Payment history, invoice status, plan changes
- **Feature Usage**: Feature interaction logs, adoption metrics
- **Support History**: Ticket volume, resolution times, satisfaction scores

## Recommendations System

Based on the health score and individual factor performance, the system generates actionable recommendations:

### For Healthy Customers (80-100)
- Explore expansion opportunities
- Introduce advanced features
- Request case studies or testimonials
- Offer referral programs

### For At-Risk Customers (60-79)
- Schedule check-in calls
- Provide additional training
- Review usage patterns
- Offer optimization consultations

### For Critical Customers (0-59)
- Immediate customer success intervention
- Executive escalation
- Detailed needs assessment
- Recovery action plan implementation

## Best Practices

### For Customer Success Teams
1. **Monitor Trends**: Focus on score direction, not just absolute values
2. **Factor Analysis**: Identify which specific factors are driving score changes
3. **Proactive Outreach**: Contact customers before they reach critical status
4. **Segmented Approach**: Tailor strategies based on customer segment and industry

### For Product Teams
1. **Feature Adoption**: Track which features correlate with higher health scores
2. **Usage Patterns**: Identify successful customer usage patterns
3. **Onboarding**: Optimize new customer experience based on health score data

### For Sales Teams
1. **Expansion Opportunities**: Target healthy customers for upsells
2. **Renewal Risk**: Prioritize at-risk and critical customers for retention efforts
3. **Reference Customers**: Leverage healthy customers for social proof

## Updating and Maintenance

- **Calculation Frequency**: Health scores are recalculated when new customer events are recorded
- **Data Freshness**: Scores reflect the most recent customer activity
- **Historical Tracking**: Previous scores are maintained for trend analysis
- **Threshold Adjustment**: Score thresholds can be adjusted based on business needs and customer success outcomes

---

*This guide should be reviewed and updated regularly to ensure alignment with business objectives and customer success strategies.*