import os
import json
import time
from pathlib import Path


class RateLimiter:
    def __init__(self, rate_dir=".rate_limits"):
        self.rate_dir = Path(rate_dir)
        self.rate_dir.mkdir(exist_ok=True)
        
        # Configuration from environment variables with defaults
        self.hourly_limit = int(os.getenv('HOURLY_LIMIT', '10'))
        self.daily_limit = int(os.getenv('DAILY_LIMIT', '25'))
        self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', '60'))
    
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
    
    def check_rate_limit(self, ip_address):
        """Check if IP address is within rate limits. Returns (allowed, message, stats)"""
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data or create new
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {'requests': [], 'last_request': 0}
        else:
            data = {'requests': [], 'last_request': 0}
        
        # Clean up old requests
        data['requests'] = self._cleanup_old_requests(data['requests'], current_time)
        
        # Check cooldown period
        if current_time - data.get('last_request', 0) < self.cooldown_seconds:
            remaining_cooldown = int(self.cooldown_seconds - (current_time - data['last_request']))
            return False, f"⏰ Please wait {remaining_cooldown} seconds between requests", self._get_usage_stats(data['requests'], current_time)
        
        # Check hourly limit
        hour_ago = current_time - 3600
        hourly_requests = [req for req in data['requests'] if req > hour_ago]
        
        if len(hourly_requests) >= self.hourly_limit:
            next_reset = int((min(hourly_requests) + 3600 - current_time) / 60)
            return False, f"Hourly limit reached ({self.hourly_limit} requests/hour). Try again in {next_reset} minutes.", self._get_usage_stats(data['requests'], current_time)
        
        # Check daily limit
        if len(data['requests']) >= self.daily_limit:
            next_reset = int((min(data['requests']) + 24*3600 - current_time) / 3600)
            return False, f"Daily limit reached ({self.daily_limit} requests/day). Try again in {next_reset} hours.", self._get_usage_stats(data['requests'], current_time)
        
        return True, "Request allowed", self._get_usage_stats(data['requests'], current_time)
    
    def record_request(self, ip_address):
        """Record a new request for the IP address"""
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {'requests': [], 'last_request': 0}
        else:
            data = {'requests': [], 'last_request': 0}
        
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