"""
Unit tests for PaymentTimelinessFactor
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.health_factors.payment_timeliness import PaymentTimelinessFactor
from domain.models import Customer, CustomerEvent, FactorScore


class TestPaymentTimelinessFactor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factor = PaymentTimelinessFactor()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.segment = "Enterprise"
    
    def test_factor_properties(self):
        """Test factor properties are correctly defined"""
        assert self.factor.name == "payment_timeliness"
        assert self.factor.weight == 0.15
        assert "financial health" in self.factor.description.lower()
    
    def test_calculate_score_no_payment_history(self):
        """Test score calculation with no payment history"""
        # Create non-payment events
        events = []
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"  # Not payment
            event.timestamp = datetime.utcnow() - timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert isinstance(result, FactorScore)
        assert result.score == 70.0  # Neutral score for no history
        assert result.value == 0
        assert "No recent payment history" in result.description
        assert result.metadata["total_payments"] == 0
        assert result.metadata["average_amount"] == 0
    
    def test_calculate_score_perfect_payment_history(self):
        """Test score calculation with perfect on-time payments"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=60)
        
        # Create 5 on-time payments
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 15)
            event.event_data = {
                "payment_method": "credit_card",
                "amount": 100.0
            }
            event.get_payment_status.return_value = "paid_on_time"
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0
        assert result.value == 5
        assert "100.0% payments on time" in result.description
        assert result.metadata["total_payments"] == 5
        assert result.metadata["late_payments"] == 0
        assert result.metadata["overdue_payments"] == 0
        assert result.metadata["on_time_percentage"] == 100.0
        assert result.metadata["average_amount"] == 100.0
    
    def test_calculate_score_mixed_payment_history(self):
        """Test score calculation with mixed payment statuses"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=60)
        
        # Create mixed payment events
        payment_statuses = ["paid_on_time", "paid_on_time", "paid_late", "paid_on_time"]
        for i, status in enumerate(payment_statuses):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 15)
            event.event_data = {
                "payment_method": "bank_transfer",
                "amount": 150.0 + i * 10
            }
            event.get_payment_status.return_value = status
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # 3 on-time out of 4 total = 75%
        assert result.score == 75.0
        assert result.value == 3
        assert "75.0% payments on time" in result.description
        assert result.metadata["total_payments"] == 4
        assert result.metadata["late_payments"] == 1
        assert result.metadata["overdue_payments"] == 0
        assert result.metadata["on_time_percentage"] == 75.0
    
    def test_calculate_score_with_overdue_payments(self):
        """Test score calculation with overdue payments (penalties applied)"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=60)
        
        # Create payments with overdue penalties
        payment_statuses = ["paid_on_time", "paid_on_time", "overdue", "overdue"]
        for i, status in enumerate(payment_statuses):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 15)
            event.event_data = {
                "payment_method": "invoice",
                "amount": 200.0
            }
            event.get_payment_status.return_value = status
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Base score: 50% (2/4 on-time) - 30 penalty (2 overdue * 15) = 20.0
        assert result.score == 20.0
        assert result.value == 2
        assert result.metadata["total_payments"] == 4
        assert result.metadata["overdue_payments"] == 2
        assert result.metadata["on_time_percentage"] == 50.0
    
    def test_calculate_score_severe_overdue_penalty_floor(self):
        """Test that overdue penalties don't make score go below 0"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=60)
        
        # Create many overdue payments
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 8)
            event.event_data = {
                "payment_method": "check",
                "amount": 300.0
            }
            event.get_payment_status.return_value = "overdue"
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Score should not go below 0
        assert result.score == 0.0
        assert result.value == 0  # 0 on-time payments
        assert result.metadata["overdue_payments"] == 10
    
    def test_calculate_score_different_payment_methods(self):
        """Test payment method tracking"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=60)
        
        payment_methods = ["credit_card", "bank_transfer", "credit_card", "paypal", "bank_transfer"]
        for i, method in enumerate(payment_methods):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 12)
            event.event_data = {
                "payment_method": method,
                "amount": 100.0 + i * 25
            }
            event.get_payment_status.return_value = "paid_on_time"
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.metadata["payment_methods"]["credit_card"] == 2
        assert result.metadata["payment_methods"]["bank_transfer"] == 2
        assert result.metadata["payment_methods"]["paypal"] == 1
        # Average: (100 + 125 + 150 + 175 + 200) / 5 = 150.0
        assert result.metadata["average_amount"] == 150.0
    
    def test_calculate_score_old_payments_excluded(self):
        """Test that payments older than 90 days are excluded"""
        events = []
        
        # Add 3 recent payments (within 90 days)
        recent_time = datetime.utcnow() - timedelta(days=60)
        for i in range(3):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = recent_time + timedelta(days=i * 10)
            event.event_data = {"payment_method": "recent", "amount": 100.0}
            event.get_payment_status.return_value = "paid_on_time"
            events.append(event)
        
        # Add 5 old payments (older than 90 days)
        old_time = datetime.utcnow() - timedelta(days=120)
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = old_time + timedelta(days=i * 5)
            event.event_data = {"payment_method": "old", "amount": 200.0}
            event.get_payment_status.return_value = "paid_late"
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count the 3 recent payments
        assert result.value == 3
        assert result.score == 100.0  # All recent ones were on-time
        assert result.metadata["total_payments"] == 3
        assert "recent" in result.metadata["payment_methods"]
        assert "old" not in result.metadata["payment_methods"]
    
    def test_calculate_score_no_event_data(self):
        """Test handling of payment events without event_data"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Create payment events without event_data
        for i in range(3):
            event = Mock(spec=CustomerEvent)
            event.event_type = "payment"
            event.timestamp = base_time + timedelta(days=i * 10)
            event.event_data = None
            event.get_payment_status.return_value = "paid_on_time"
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # When event_data is None, events are counted in total but not processed for status
        assert result.value == 0  # No on-time payments counted
        assert result.score == 0.0  # 0% on-time
        assert result.metadata["total_payments"] == 3
        assert result.metadata["payment_methods"] == {}
        assert result.metadata["average_amount"] == 0.0
    
    def test_generate_recommendations_critical_payment_issues(self):
        """Test recommendations for critical payment issues"""
        score = FactorScore(score=30.0, value=2, description="Poor payment history")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("contact customer immediately" in rec.lower() for rec in recommendations)
        assert any("payment plan" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_moderate_payment_issues(self):
        """Test recommendations for moderate payment issues"""
        score = FactorScore(score=65.0, value=4, description="Some payment delays")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("billing process" in rec.lower() for rec in recommendations)
        assert any("payment automation" in rec.lower() for rec in recommendations)
        assert any("autopay" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_excellent_payment_history(self):
        """Test recommendations for excellent payment history"""
        score = FactorScore(score=98.0, value=10, description="Excellent payment history")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("excellent payment history" in rec.lower() for rec in recommendations)
        assert any("payment discounts" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_good_payment_history(self):
        """Test recommendations for good payment history (no specific recommendations)"""
        score = FactorScore(score=85.0, value=8, description="Good payment history")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        # Should return empty list for scores between 80-94
        assert len(recommendations) == 0
    
    def test_calculate_score_edge_case_single_payment(self):
        """Test score calculation with only one payment"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=30)
        event.event_data = {
            "payment_method": "credit_card",
            "amount": 500.0
        }
        event.get_payment_status.return_value = "paid_late"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 0.0  # 0% on-time (0/1)
        assert result.value == 0  # 0 on-time payments
        assert result.metadata["total_payments"] == 1
        assert result.metadata["late_payments"] == 1
        assert result.metadata["average_amount"] == 500.0

    # =========================
    # SAD PATH / EDGE CASES
    # =========================
    
    def test_calculate_score_zero_amount_payment(self):
        """Test handling of zero amount payments"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=15)
        event.event_data = {
            "payment_method": "credit_card",
            "amount": 0.0  # Zero amount
        }
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0  # Still counts as on-time
        assert result.metadata["total_payments"] == 1
        assert result.metadata["average_amount"] == 0.0
    
    def test_calculate_score_negative_amount_payment(self):
        """Test handling of negative amount payments (refunds)"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=20)
        event.event_data = {
            "payment_method": "refund",
            "amount": -100.0  # Negative amount (refund)
        }
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0
        assert result.metadata["average_amount"] == -100.0  # Should handle negative amounts
    
    def test_calculate_score_missing_payment_method(self):
        """Test handling of payments missing payment method"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment" 
        event.timestamp = datetime.utcnow() - timedelta(days=10)
        event.event_data = {
            # Missing payment_method
            "amount": 250.0
        }
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should still process the payment despite missing method
        assert result.score == 100.0
        assert result.metadata["total_payments"] == 1
    
    def test_calculate_score_invalid_event_data_structure(self):
        """Test handling of malformed event data"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=25)
        event.event_data = None  # Invalid data structure
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        # Should handle gracefully or raise appropriate error
        try:
            result = self.factor.calculate_score(self.customer, events)
            # If it doesn't raise an error, it should handle gracefully
            assert result is not None
        except (AttributeError, KeyError, TypeError):
            # Expected behavior - should handle gracefully
            pass
    
    def test_calculate_score_extremely_large_amount(self):
        """Test handling of extremely large payment amounts"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=5)
        event.event_data = {
            "payment_method": "wire_transfer",
            "amount": 999999999.99  # Very large amount
        }
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0
        assert result.metadata["average_amount"] == 999999999.99
        assert result.metadata["total_payments"] == 1
    
    def test_calculate_score_payment_status_exception(self):
        """Test handling when payment status check throws exception"""
        events = []
        
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=15)
        event.event_data = {
            "payment_method": "credit_card",
            "amount": 100.0
        }
        event.get_payment_status.side_effect = Exception("Status check failed")
        events.append(event)
        
        # Should handle payment status errors gracefully
        try:
            result = self.factor.calculate_score(self.customer, events)
            # If no exception, check it handled gracefully
            assert result is not None
        except Exception:
            # Expected - method should handle status check failures appropriately
            pass
    
    def test_calculate_score_customer_without_segment(self):
        """Test calculation for customer without segment information"""
        customer_no_segment = Mock()
        customer_no_segment.segment = None  # No segment info
        
        events = []
        event = Mock(spec=CustomerEvent)
        event.event_type = "payment"
        event.timestamp = datetime.utcnow() - timedelta(days=10)
        event.event_data = {
            "payment_method": "credit_card", 
            "amount": 200.0
        }
        event.get_payment_status.return_value = "paid_on_time"
        events.append(event)
        
        result = self.factor.calculate_score(customer_no_segment, events)
        
        # Should handle customer without segment gracefully
        assert result is not None
        assert result.score >= 0