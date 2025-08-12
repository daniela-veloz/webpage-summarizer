import os
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
from enum import Enum

from backend.ip_extractor import IPExtractor

DEFAULT_HOUR_LIMIT = 10
DEFAULT_DAILY_LIMIT = 25
DEFAULT_COOLDOWN_SECONDS = 60


class RateLimitType(Enum):
    """Types of rate limit violations"""
    NONE = "none"
    COOLDOWN = "cooldown"
    HOURLY_LIMIT = "hourly_limit"
    DAILY_LIMIT = "daily_limit"


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    valid: bool
    limit_type: RateLimitType
    remaining_cooldown: int
    next_reset: int
    stats: Dict[str, Any]

class RateLimiter:
    def __init__(self, rate_dir=".rate_limits"):
        self.rate_dir = Path(rate_dir)
        self.rate_dir.mkdir(exist_ok=True)
        
        # Configuration from environment variables with defaults
        self.hourly_limit = int(os.getenv('HOURLY_LIMIT', DEFAULT_HOUR_LIMIT))
        self.daily_limit = int(os.getenv('DAILY_LIMIT', DEFAULT_DAILY_LIMIT))
        self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', DEFAULT_COOLDOWN_SECONDS))
    
    def _get_ip_file(self, ip_address):
        # Clean IP for filename (replace dots/colons with underscores)
        clean_ip = ip_address.replace('.', '_').replace(':', '_')
        return self.rate_dir / f"ip_{clean_ip}.json"
    
    def _get_current_time(self):
        return time.time()
    
    def _cleanup_old_requests(self, requests_data, current_time):
        """Remove requests older than 24 hours"""
        cutoff_time = current_time - (24 * 3600)  # 24 hours ago
        return [req_time for req_time in requests_data if req_time > cutoff_time]
    
    def _get_reminder_cooldown(self, data, current_time) -> int:
        """Check if request is within cooldown period"""
        if current_time - data.get('last_request', 0) < self.cooldown_seconds:
            return int(self.cooldown_seconds - (current_time - data['last_request']))
        return 0
    
    def _get_next_reset(self, data, current_time) -> int:
        """Check hourly and daily rate limits"""
        # Check hourly limit
        hour_ago = current_time - 3600
        hourly_requests = [req for req in data['requests'] if req > hour_ago]
        
        if len(hourly_requests) >= self.hourly_limit:
            return int((min(hourly_requests) + 3600 - current_time) / 60)

        # Check daily limit
        if len(data['requests']) >= self.daily_limit:
            return int((min(data['requests']) + 24*3600 - current_time) / 3600)

        return 0
    
    def check_rate_limit(self):
        """Check if IP address is within rate limits"""
        ip_address = IPExtractor.get_client_ip()
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data or create new
        data = self._load_ip_data(ip_file)
        
        # Clean up old requests
        data['requests'] = self._cleanup_old_requests(data['requests'], current_time)
        
        # Check cooldown period
        reminder_cooldown = self._get_reminder_cooldown(data, current_time)
        
        # Check rate limits
        next_reset = self._get_next_reset(data, current_time)

        is_valid = reminder_cooldown == 0 and next_reset == 0
        limit_type = RateLimitType.NONE if is_valid else (
            RateLimitType.COOLDOWN if reminder_cooldown > 0 else
            RateLimitType.HOURLY_LIMIT if next_reset < 60 else
            RateLimitType.DAILY_LIMIT
        )
        
        return RateLimitResult(
            valid=is_valid,
            limit_type=limit_type,
            remaining_cooldown=reminder_cooldown,
            next_reset=next_reset,
            stats=self._get_usage_stats(data['requests'], current_time)
        )

    def record_request(self, ip_address):
        """Record a new request for the IP address"""
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data
        data = self._load_ip_data(ip_file)
        
        # Add new request and update last request time
        data['requests'].append(current_time)
        data['last_request'] = current_time
        
        # Clean up old requests
        data['requests'] = self._cleanup_old_requests(data['requests'], current_time)
        
        # Save updated data
        try:
            with open(ip_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save rate limit data: {e}")
    
    def _load_ip_data(self, ip_file):
        """Load IP data from file or return default structure"""
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {'requests': [], 'last_request': 0}
        else:
            return {'requests': [], 'last_request': 0}

    def _get_usage_stats(self, requests, current_time):
        """Get current usage statistics"""
        hour_ago = current_time - 3600
        hourly_count = len([req for req in requests if req > hour_ago])
        daily_count = len(requests)
        
        return {
            'hourly_used': hourly_count,
            'hourly_limit': self.hourly_limit,
            'daily_used': daily_count,
            'daily_limit': self.daily_limit,
            'hourly_remaining': max(0, self.hourly_limit - hourly_count),
            'daily_remaining': max(0, self.daily_limit - daily_count)
        }


