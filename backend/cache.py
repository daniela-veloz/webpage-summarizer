import hashlib
import json
import time
from pathlib import Path


class URLCache:
    """
    File-based caching system for URL summaries.
    
    This class provides a simple file-based cache that stores webpage summaries
    with automatic expiration. Cache keys are generated using MD5 hashes of URLs,
    and cached data includes timestamps for expiration management.
    
    Attributes:
        cache_dir (Path): Directory for storing cache files
        cache_hours (int): Cache expiration time in hours
    """
    def __init__(self, cache_dir=".cache", cache_hours=24):
        """
        Initialize the URL cache.
        
        Args:
            cache_dir (str): Directory path for storing cache files.
                           Defaults to '.cache'.
            cache_hours (int): Cache expiration time in hours.
                             Defaults to 24 hours.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_enabled = True
        try:
            self.cache_dir.mkdir(exist_ok=True)
        except PermissionError:
            print(f"Warning: Cannot create cache directory {cache_dir}. Caching disabled.")
            self.cache_enabled = False
        self.cache_hours = cache_hours
    
    def _get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, url):
        """
        Retrieve a cached summary for the given URL.
        
        Checks if a valid (non-expired) cache entry exists for the URL.
        Automatically removes expired cache files.
        
        Args:
            url (str): The URL to look up in cache
            
        Returns:
            str or None: The cached summary if found and valid, None otherwise
        """
        if not self.cache_enabled:
            return None
            
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
        """
        Store a summary in the cache for the given URL.
        
        Creates a cache entry with the current timestamp for expiration tracking.
        Handles file writing errors gracefully by continuing without caching.
        
        Args:
            url (str): The URL to cache the summary for
            summary (str): The summary content to cache
        """
        if not self.cache_enabled:
            return
            
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