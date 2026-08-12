"""
Semantic Models for Donor Management Domain

This module provides access to semantic models used by the Donor Management domain.
It demonstrates how to consume business metrics through semantic models rather than direct table access.
"""

from typing import Dict, List, Any, Optional
from platform.connectivity import (
    FabricConnectionManager, 
    SemanticModelManager,
    SemanticModelAccess,
    get_connection_manager,
    get_semantic_model_manager,
    semantic_model_execute,
    ConnectionConfig,
    ConnectionType,
    AuthenticationType
)
from platform.config import get_config_value


# Initialize semantic model access
semantic_model = SemanticModelAccess(get_semantic_model_manager())


def get_donor_semantic_model():
    """
    Get the Donor semantic model connection
    
    Returns:
        Semantic model connection for donor data
    """
    return semantic_model_execute(
        model_name="DonorSemanticModel",
        query="EVALUATE Donors"
    )


def get_campaign_semantic_model():
    """
    Get the Campaign semantic model connection
    
    Returns:
        Semantic model connection for campaign data
    """
    return semantic_model_execute(
        model_name="CampaignSemanticModel",
        query="EVALUATE Campaigns"
    )


class DonorSemanticModel:
    """
    Convenience class for accessing Donor semantic model
    
    Provides domain-specific methods for common donor queries.
    """
    
    MODEL_NAME = "DonorSemanticModel"
    
    @classmethod
    def get_donor_by_id(cls, donor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific donor by ID
        
        Args:
            donor_id: The ID of the donor
            
        Returns:
            Dictionary containing donor information, or None if not found
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Donor with ID {donor_id}"
        )
        
        if result.result.data:
            return result.result.data[0]
        return None
    
    @classmethod
    def get_donors_by_classification(cls, classification: str) -> List[Dict[str, Any]]:
        """
        Get all donors with a specific classification
        
        Args:
            classification: Donor classification (Platinum, Gold, Silver, Bronze)
            
        Returns:
            List of donors with the specified classification
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Donors with Classification {classification}"
        )
        
        return result.result.data if result.result.data else []
    
    @classmethod
    def get_donor_contribution_history(cls, donor_id: str, years: int = 5) -> List[Dict[str, Any]]:
        """
        Get contribution history for a donor
        
        Args:
            donor_id: The ID of the donor
            years: Number of years of history to retrieve
            
        Returns:
            List of contribution records
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Contribution History for Donor {donor_id} (Last {years} years)",
            parameters={"years": years}
        )
        
        return result.result.data if result.result.data else []
    
    @classmethod
    def get_donor_engagement_metrics(cls, donor_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a donor
        
        Args:
            donor_id: The ID of the donor
            
        Returns:
            Dictionary containing engagement metrics
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Engagement Metrics for Donor {donor_id}"
        )
        
        if result.result.data:
            return result.result.data[0]
        return {}
    
    @classmethod
    def get_top_donors(cls, limit: int = 10, by: str = "total_contributions") -> List[Dict[str, Any]]:
        """
        Get top donors by a specific metric
        
        Args:
            limit: Maximum number of donors to return
            by: Metric to sort by (total_contributions, average_contribution, frequency)
            
        Returns:
            List of top donors
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Top {limit} Donors by {by.replace('_', ' ').title()}",
            parameters={"limit": limit, "sort_by": by}
        )
        
        return result.result.data if result.result.data else []


class CampaignSemanticModel:
    """
    Convenience class for accessing Campaign semantic model
    
    Provides domain-specific methods for common campaign queries.
    """
    
    MODEL_NAME = "CampaignSemanticModel"
    
    @classmethod
    def get_campaign_by_id(cls, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific campaign by ID
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            Dictionary containing campaign information, or None if not found
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Campaign with ID {campaign_id}"
        )
        
        if result.result.data:
            return result.result.data[0]
        return None
    
    @classmethod
    def get_campaigns_by_status(cls, status: str) -> List[Dict[str, Any]]:
        """
        Get all campaigns with a specific status
        
        Args:
            status: Campaign status (Planning, Active, Completed, Cancelled)
            
        Returns:
            List of campaigns with the specified status
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Campaigns with Status {status}"
        )
        
        return result.result.data if result.result.data else []
    
    @classmethod
    def get_campaign_performance(cls, campaign_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a campaign
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            Dictionary containing campaign performance metrics
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Performance Metrics for Campaign {campaign_id}"
        )
        
        if result.result.data:
            return result.result.data[0]
        return {}
    
    @classmethod
    def get_donor_campaign_participation(cls, donor_id: str) -> List[Dict[str, Any]]:
        """
        Get all campaigns a donor has participated in
        
        Args:
            donor_id: The ID of the donor
            
        Returns:
            List of campaigns the donor has participated in
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Campaign Participation for Donor {donor_id}"
        )
        
        return result.result.data if result.result.data else []


class RevenueSemanticModel:
    """
    Convenience class for accessing Revenue semantic model
    
    Provides methods for revenue-related queries.
    """
    
    MODEL_NAME = "RevenueSemanticModel"
    
    @classmethod
    def get_revenue_by_donor(cls, donor_id: str, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get revenue information for a specific donor
        
        Args:
            donor_id: The ID of the donor
            year: Optional year filter
            
        Returns:
            Dictionary containing revenue information
        """
        query = f"Revenue for Donor {donor_id}"
        if year:
            query += f" in {year}"
        
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=query
        )
        
        if result.result.data:
            return result.result.data[0]
        return {}
    
    @classmethod
    def get_revenue_forecast(cls, period: str = "quarter", years: int = 1) -> Dict[str, Any]:
        """
        Get revenue forecast for a specific period
        
        Args:
            period: Forecast period (quarter, year, month)
            years: Number of years to forecast
            
        Returns:
            Dictionary containing revenue forecast
        """
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=f"Revenue Forecast for Next {years} {period.title()}(s)",
            parameters={"period": period, "years": years}
        )
        
        if result.result.data:
            return result.result.data[0]
        return {}
    
    @classmethod
    def get_revenue_by_region(cls, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get revenue breakdown by region
        
        Args:
            year: Optional year filter
            
        Returns:
            List of regions with their revenue data
        """
        query = "Revenue by Region"
        if year:
            query += f" in {year}"
        
        result = semantic_model_execute(
            model_name=cls.MODEL_NAME,
            query=query
        )
        
        return result.result.data if result.result.data else []


# Example usage functions
def get_donor_portfolio_summary(donor_id: str) -> Dict[str, Any]:
    """
    Get a comprehensive portfolio summary for a donor
    
    This function demonstrates how to combine data from multiple semantic models
    to create a rich domain-specific response.
    
    Args:
        donor_id: The ID of the donor
        
    Returns:
        Dictionary containing comprehensive portfolio summary
    """
    # Get donor basic information
    donor = DonorSemanticModel.get_donor_by_id(donor_id)
    if not donor:
        return {"error": "Donor not found"}
    
    # Get contribution history
    contributions = DonorSemanticModel.get_donor_contribution_history(donor_id)
    
    # Get engagement metrics
    engagement = DonorSemanticModel.get_donor_engagement_metrics(donor_id)
    
    # Get campaign participation
    campaigns = CampaignSemanticModel.get_donor_campaign_participation(donor_id)
    
    # Get revenue information
    revenue = RevenueSemanticModel.get_revenue_by_donor(donor_id)
    
    # Combine all data into a comprehensive summary
    return {
        "donor_id": donor_id,
        "donor_name": donor.get("name", "Unknown"),
        "classification": donor.get("classification", "Unknown"),
        "status": donor.get("status", "Unknown"),
        
        "contribution_summary": {
            "total_contributions": sum(c.get("amount", 0) for c in contributions),
            "contribution_count": len(contributions),
            "average_contribution": sum(c.get("amount", 0) for c in contributions) / len(contributions) if contributions else 0,
            "last_contribution_date": contributions[0].get("date") if contributions else None
        },
        
        "engagement_metrics": engagement,
        
        "campaign_participation": {
            "total_campaigns": len(campaigns),
            "active_campaigns": len([c for c in campaigns if c.get("status") == "Active"]),
            "completed_campaigns": len([c for c in campaigns if c.get("status") == "Completed"])
        },
        
        "revenue_impact": revenue,
        
        "portfolio_health": {
            "health_score": calculate_health_score(donor, contributions, engagement, campaigns),
            "risk_level": determine_risk_level(donor, contributions),
            "recommendations": generate_recommendations(donor, contributions, engagement)
        }
    }


def calculate_health_score(donor: Dict, contributions: List[Dict], 
                         engagement: Dict, campaigns: List[Dict]) -> float:
    """
    Calculate a health score for a donor portfolio
    
    This is a simplified example - in production, this would use a more sophisticated algorithm.
    """
    score = 0.0
    
    # Base score from classification
    classification_scores = {
        "Platinum": 30,
        "Gold": 25,
        "Silver": 20,
        "Bronze": 15
    }
    score += classification_scores.get(donor.get("classification", "Bronze"), 0)
    
    # Contribution frequency (max 20 points)
    contribution_count = len(contributions)
    if contribution_count >= 12:
        score += 20
    elif contribution_count >= 6:
        score += 15
    elif contribution_count >= 3:
        score += 10
    elif contribution_count >= 1:
        score += 5
    
    # Engagement score (max 20 points)
    engagement_score = engagement.get("score", 0)
    score += min(engagement_score * 0.2, 20)
    
    # Campaign participation (max 15 points)
    active_campaigns = len([c for c in campaigns if c.get("status") == "Active"])
    score += min(active_campaigns * 5, 15)
    
    # Recent activity (max 10 points)
    if contributions:
        last_contribution = contributions[0].get("date")
        # Simple check - in production, calculate days since last contribution
        score += 10
    
    return min(score, 100.0)


def determine_risk_level(donor: Dict, contributions: List[Dict]) -> str:
    """
    Determine the risk level for a donor portfolio
    """
    if not contributions:
        return "High"
    
    # Check for recent activity
    if contributions:
        last_contribution = contributions[0].get("date")
        # In production, check if last contribution was recent
        if not last_contribution:
            return "High"
    
    # Check classification
    classification = donor.get("classification", "Bronze")
    if classification in ["Platinum", "Gold"]:
        return "Low"
    elif classification == "Silver":
        return "Medium"
    else:
        return "Medium"


def generate_recommendations(donor: Dict, contributions: List[Dict], 
                           engagement: Dict) -> List[str]:
    """
    Generate recommendations for improving donor portfolio health
    """
    recommendations = []
    
    # Check contribution frequency
    if len(contributions) < 3:
        recommendations.append("Increase contribution frequency to improve engagement")
    
    # Check engagement score
    if engagement.get("score", 0) < 70:
        recommendations.append("Improve engagement through targeted communications")
    
    # Check classification
    classification = donor.get("classification", "Bronze")
    if classification == "Bronze":
        recommendations.append("Consider upgrading to Silver classification based on contribution history")
    
    # Add generic recommendations
    recommendations.extend([
        "Schedule regular check-ins with the donor",
        "Provide updates on the impact of their contributions",
        "Invite to exclusive events based on their giving level"
    ])
    
    return recommendations
