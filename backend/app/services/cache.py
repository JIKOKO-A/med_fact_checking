import logging,json,hashlib
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.memory_cache = {}
        self.redis_available = False
        import os
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            import redis
            # Parse URL or use defaults
            if "://" in redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.client = redis.Redis(host="redis", port=6379, decode_responses=True)
            self.client.ping()
            self.redis_available = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            self.client = None
            logger.warning(f"⚠️ Redis connection failed: {e}. Using memory cache.")
    
    def set(self, key: str, value: Dict) -> bool:
        if self.redis_available and self.client:
            try:
                self.client.set(key, json.dumps(value), ex=86400) # Expire in 24 hours
                return True
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
                
        self.memory_cache[key] = value
        return True
    
    def get(self, key: str) -> Optional[Dict]:
        if self.redis_available and self.client:
            try:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
                
        return self.memory_cache.get(key)
    
    def cache_verification_result(self, text: str, result: Dict) -> bool:
        key = "verification:" + hashlib.sha256(text.encode()).hexdigest()
        return self.set(key, result)
    
    def get_cached_verification(self, text: str) -> Optional[Dict]:
        key = "verification:" + hashlib.sha256(text.encode()).hexdigest()
        return self.get(key)
    
    def is_healthy(self) -> bool:
        return True
    
    def get_stats(self) -> Dict:
        return {"status": "healthy", "cache_size": len(self.memory_cache), "redis": self.redis_available}

cache_service = CacheService()
