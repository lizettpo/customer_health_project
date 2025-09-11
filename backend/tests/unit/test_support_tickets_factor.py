"""
Unit tests for SupportTicketsFactor
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.health_factors.support_tickets import SupportTicketsFactor
from domain.models import Customer, CustomerEvent, FactorScore


class TestSupportTicketsFactor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factor = SupportTicketsFactor()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.segment = "Enterprise"
    
    def test_factor_properties(self):
        """Test factor properties are correctly defined"""
        assert self.factor.name == "support_tickets"
        assert self.factor.weight == 0.20
        assert "friction" in self.factor.description.lower()
        assert "inverse" in self.factor.description.lower()
    
    def test_calculate_score_no_tickets(self):
        """Test score calculation with no support tickets (perfect score)"""
        # Create non-support-ticket events
        events = []
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"  # Not support_ticket
            event.timestamp = datetime.utcnow() - timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert isinstance(result, FactorScore)
        assert result.score == 100.0
        assert result.value == 0
        assert "0 support tickets" in result.description
        assert result.metadata["interpretation"] == "Lower ticket count indicates better product experience"
    
    def test_calculate_score_low_tickets(self):
        """Test score calculation with low ticket count (1-2 tickets)"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=15)
        
        # Create 2 support tickets
        for i in range(2):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 7)
            event.event_data = {
                "ticket_type": "question",
                "priority": "low"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 80.0
        assert result.value == 2
        assert "2 support tickets" in result.description
        assert result.metadata["priorities"]["low"] == 2
    
    def test_calculate_score_medium_tickets(self):
        """Test score calculation with medium ticket count (3-4 tickets)"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        # Create 4 support tickets
        for i in range(4):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 5)
            event.event_data = {
                "ticket_type": "bug_report",
                "priority": "medium"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 60.0
        assert result.value == 4
        assert result.metadata["priorities"]["medium"] == 4
        assert result.metadata["ticket_types"]["bug_report"] == 4
    
    def test_calculate_score_high_tickets(self):
        """Test score calculation with high ticket count (5-6 tickets)"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=25)
        
        # Create 6 support tickets
        for i in range(6):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 4)
            event.event_data = {
                "ticket_type": "technical_issue",
                "priority": "high"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Base score 40.0 - (6 high priority tickets * 5 penalty) = 40.0 - 30 = 10.0
        assert result.score == 10.0
        assert result.value == 6
        assert result.metadata["priorities"]["high"] == 6
    
    def test_calculate_score_very_high_tickets(self):
        """Test score calculation with very high ticket count (>6 tickets)"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=25)
        
        # Create 10 support tickets
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 2)
            event.event_data = {
                "ticket_type": "complaint",
                "priority": "medium"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Base score: 40.0 - (10 - 6) * 5 = 40.0 - 20 = 20.0
        assert result.score == 20.0
        assert result.value == 10
        assert result.metadata["ticket_types"]["complaint"] == 10
    
    def test_calculate_score_urgent_tickets_penalty(self):
        """Test penalty application for urgent tickets"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=15)
        
        # Create 2 urgent tickets (should be 80.0 base - 20 penalty = 60.0)
        for i in range(2):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 7)
            event.event_data = {
                "ticket_type": "critical_issue",
                "priority": "urgent"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Base score 80.0 - (2 urgent tickets * 10 penalty) = 80.0 - 20 = 60.0
        assert result.score == 60.0
        assert result.value == 2
        assert result.metadata["priorities"]["urgent"] == 2
    
    def test_calculate_score_mixed_priority_tickets(self):
        """Test score calculation with mixed priority tickets"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        # Create tickets with different priorities
        priorities = ["low", "medium", "high", "urgent"]
        for i, priority in enumerate(priorities):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i * 5)
            event.event_data = {
                "ticket_type": f"issue_{i}",
                "priority": priority
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Base score 60.0 (4 tickets) - 5 (1 high) - 10 (1 urgent) = 45.0
        assert result.score == 45.0
        assert result.value == 4
        assert result.metadata["priorities"]["low"] == 1
        assert result.metadata["priorities"]["medium"] == 1
        assert result.metadata["priorities"]["high"] == 1
        assert result.metadata["priorities"]["urgent"] == 1
    
    def test_calculate_score_old_tickets_excluded(self):
        """Test that tickets older than 30 days are excluded"""
        events = []
        
        # Add 3 recent tickets (within 30 days)
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i in range(3):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = recent_time + timedelta(days=i * 5)
            event.event_data = {"ticket_type": "recent", "priority": "low"}
            events.append(event)
        
        # Add 5 old tickets (older than 30 days)
        old_time = datetime.utcnow() - timedelta(days=35)
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = old_time + timedelta(days=i)
            event.event_data = {"ticket_type": "old", "priority": "high"}
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count the 3 recent tickets
        assert result.value == 3
        assert result.score == 60.0  # 3 tickets = 60.0
        assert "recent" in result.metadata["ticket_types"]
        assert "old" not in result.metadata["ticket_types"]
    
    def test_calculate_score_no_event_data(self):
        """Test handling of tickets without event_data"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=10)
        
        # Create tickets without event_data
        for i in range(3):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(days=i)
            event.event_data = None
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.value == 3
        assert result.score == 60.0
        assert "unknown" in result.metadata["ticket_types"]
        assert result.metadata["priorities"]["medium"] == 3  # Default priority
    
    def test_calculate_score_minimum_score_cap(self):
        """Test that score doesn't go below minimum with severe penalties"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        # Create many urgent tickets to test score floor
        for i in range(15):
            event = Mock(spec=CustomerEvent)
            event.event_type = "support_ticket"
            event.timestamp = base_time + timedelta(hours=i)
            event.event_data = {
                "ticket_type": "critical",
                "priority": "urgent"
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Score should not go below 0
        assert result.score >= 0.0
        assert result.value == 15
    
    def test_generate_recommendations_critical_tickets(self):
        """Test recommendations for critical high ticket volume"""
        score = FactorScore(score=30.0, value=8, description="High ticket volume")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("recurring issues" in rec.lower() for rec in recommendations)
        assert any("dedicated customer success" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_moderate_tickets(self):
        """Test recommendations for moderate ticket volume"""
        score = FactorScore(score=60.0, value=4, description="Moderate ticket volume")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("proactive outreach" in rec.lower() for rec in recommendations)
        assert any("preventive resources" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_perfect_score(self):
        """Test recommendations for perfect score (no tickets)"""
        score = FactorScore(score=100.0, value=0, description="No tickets")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("excellent" in rec.lower() for rec in recommendations)
        assert any("zero support tickets" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_good_score(self):
        """Test recommendations for good score (no specific recommendations)"""
        score = FactorScore(score=80.0, value=2, description="Low ticket volume")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        # Should return empty list for scores between 70-99
        assert len(recommendations) == 0