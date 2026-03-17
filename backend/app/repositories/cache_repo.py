import hashlib
import json
import logging
import os
from typing import Optional

import redis
from redis import Redis

logger = logging.getLogger(__name__)


class CacheRepository:
    """Repository for Redis cache operations with fail-safe support."""

    def __init__(self):
        """Initialize Redis connection from environment variable."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.client: Optional[Redis] = redis.from_url(redis_url, decode_responses=True)
            
            self.client.ping()
            logger.info("Redis connection established")
            self.available = True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache will be disabled")
            self.client = None
            self.available = False

    def generate_key(self, question: str, history: str) -> str:
        """
        Generate cache key from question and history using MD5 hash.
        
        Args:
            question: User question
            history: Conversation history string
            
        Returns:
            MD5 hash string as cache key
        """
        try:
            combined = f"{question}:{history}"
            hash_digest = hashlib.md5(combined.encode()).hexdigest()
            return f"rag_answer:{hash_digest}"
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return ""

    def get_cached_answer(self, cache_key: str) -> Optional[dict]:
        """
        Retrieve cached answer from Redis.
        
        Args:
            cache_key: Cache key to retrieve
            
        Returns:
            Dictionary with answer and sources, or None if not found or error
        """
        if not self.available or not cache_key:
            return None
            
        try:
            cached_data = self.client.get(cache_key)
            if cached_data:
                parsed = json.loads(cached_data)
                logger.info(f"Cache HIT: Retrieved answer from Redis")
                return parsed
            return None
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
            return None

    def set_cached_answer(self, cache_key: str, answer_data: dict, ttl: int = 86400) -> bool:
        """
        Store answer in Redis with TTL (Time To Live).
        
        Args:
            cache_key: Cache key to store
            answer_data: Dictionary with answer and sources
            ttl: Time to live in seconds (default: 1 day = 86400 seconds)
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.available or not cache_key:
            return False
            
        try:
            json_data = json.dumps(answer_data)
            self.client.setex(cache_key, ttl, json_data)
            logger.info(f"Cache MISS: Stored answer in Redis (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Error storing cache: {e}")
            return False
