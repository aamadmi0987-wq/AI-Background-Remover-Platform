import json

import redis

from app.core.config import settings


QUEUE_NAME = "bg_removal_jobs"


class JobQueue:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def enqueue(self, payload: dict):
        self.redis.rpush(QUEUE_NAME, json.dumps(payload))
