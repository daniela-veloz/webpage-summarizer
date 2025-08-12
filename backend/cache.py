import hashlib
import json
import time
from pathlib import Path


class URLCache:
    def __init__(self, cache_dir=".cache", cache_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours
    
    def _get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, url):
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache has expired
            cache_time = data.get('timestamp', 0)
            current_time = time.time()
            
            if current_time - cache_time > (self.cache_hours * 3600):
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data.get('summary')
        except (json.JSONDecodeError, KeyError):
            # If cache file is corrupted, delete it
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, url, summary):
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        data = {
            'url': url,
            'summary': summary,
            'timestamp': time.time()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # If we can't write to cache, just continue without caching
            print(f"Warning: Could not write to cache: {e}")