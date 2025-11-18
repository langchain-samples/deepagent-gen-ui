"""
Research Subagent

Provides data fetching capabilities for sales and user analytics.
Returns raw data to the main agent for processing and report generation.
"""

from datetime import datetime, timedelta

from langchain.tools import tool


# =============================================================================
# MOCK DATA TOOLS
# =============================================================================

@tool
def get_sales_data(period: str = "monthly") -> dict:
    """
    Get mock sales data for report generation.
    
    Args:
        period: Time period for the data (daily, weekly, monthly, yearly)
    
    Returns:
        Dictionary containing sales data with dates, products, amounts, and regions
    """
    data = {
        "dates": ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05"],
        "products": ["Widget A", "Widget B", "Widget C", "Widget A", "Widget B"],
        "amounts": [15000, 23000, 18500, 21000, 19500],
        "regions": ["North", "South", "East", "West", "North"],
        "units_sold": [150, 230, 185, 210, 195]
    }
    return data


@tool
def get_user_analytics(metric: str = "engagement") -> dict:
    """
    Get mock user analytics data for report generation.
    
    Args:
        metric: Type of analytics to retrieve (engagement, retention, growth)
    
    Returns:
        Dictionary containing user analytics data
    """
    data = {
        "dates": [
            (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=23)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=16)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d")
        ],
        "active_users": [1250, 1380, 1520, 1450, 1600],
        "new_signups": [85, 92, 110, 88, 95],
        "retention_rate": [78.5, 80.2, 79.8, 81.5, 82.1]
    }
    return data



# =============================================================================
# RESEARCH SUBAGENT
# =============================================================================

RESEARCH_SYSTEM_PROMPT = """You are a data research specialist. Your job is to fetch and return data when requested.

You have access to:
- get_sales_data(): Retrieves sales data including dates, products, amounts, regions, and units sold
- get_user_analytics(): Retrieves user analytics including active users, new signups, and retention rates

When asked for data:
1. Determine which data source is needed based on the request
2. Call the appropriate tool to fetch the data
3. Return the data clearly to the main agent

Always be clear about what data you're returning and provide any relevant context about the data structure."""

# Create dictionary-based subagent (used by DeepAgents)
research_subagent = {
    "name": "research-specialist",
    "description": "Fetches sales data and user analytics data. Returns raw data to the main agent for report generation.",
    "tools": [
        get_sales_data,
        get_user_analytics
    ],
    "system_prompt": RESEARCH_SYSTEM_PROMPT,
    "model": "anthropic:claude-haiku-4-5"
}