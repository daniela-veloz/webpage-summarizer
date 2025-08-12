from typing import Dict, Any
from backend.rate_limiter import RateLimitResult, RateLimitType


class UIMessageHandler:
    """Handles formatting of user-facing messages and UI presentation"""
    
    @staticmethod
    def format_rate_limit_error(result: RateLimitResult) -> str:
        """Format rate limit error message for UI display"""
        message = ""
        
        if result.limit_type == RateLimitType.COOLDOWN:
            message = f"⏰ Please wait {result.remaining_cooldown} seconds between requests"
        elif result.limit_type == RateLimitType.HOURLY_LIMIT:
            message = f"Hourly limit reached. Try again in {result.next_reset} minutes."
        elif result.limit_type == RateLimitType.DAILY_LIMIT:
            message = f"Daily limit reached. Try again in {result.next_reset} hours."
        
        stats_text = UIMessageHandler.format_usage_stats(result.stats)
        tip_text = "*💡 Tip: Repeated requests to the same URL use cached results and don't count against your limit!*"
        
        return f"{message}\n\n{stats_text}\n\n{tip_text}"
    
    @staticmethod
    def format_usage_stats(stats: Dict[str, Any]) -> str:
        """Format usage statistics for UI display"""
        return (f"**Your current usage:**\n"
                f"- Hourly: {stats['hourly_used']}/{stats['hourly_limit']} "
                f"(remaining: {stats['hourly_remaining']})\n"
                f"- Daily: {stats['daily_used']}/{stats['daily_limit']} "
                f"(remaining: {stats['daily_remaining']})")
    
    @staticmethod
    def format_summary_with_stats(summary: str, stats: Dict[str, Any]) -> str:
        """Format summary with usage stats footer"""
        stats_footer = f"*📊 Usage: {stats['hourly_used']}/{stats['hourly_limit']} hourly, {stats['daily_used']}/{stats['daily_limit']} daily*"
        return f"{summary}\n\n---\n{stats_footer}"
    
    @staticmethod
    def format_cached_result(summary: str) -> str:
        """Format cached result message"""
        return f"**Cached Result** \n\n{summary}"
    
    @staticmethod
    def format_error(error: Exception) -> str:
        """Format error message for UI display"""
        return f"Error processing URL: {str(error)}"