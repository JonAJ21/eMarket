from abc import ABC
import json
from typing import Any, Callable
from redis.asyncio import Redis

class BasePubSub(ABC):
    async def publish(self, *, client):
        ...
    
    async def publish(self, channel: str, message: Any) -> int:
        ...
    
    async def subscribe(self, *, channel: str, callback: Callable[[str, Any], None]) -> None:
        ...
        
    async def close(self) -> None:
        ...

class RedisPubSub(BasePubSub):
    def __init__(self, *, client: Redis):
        self._client = client
        
    async def publish(self, channel: str, message: Any) -> int:
        await self._client.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str, callback: Callable[[str, Any], None]) -> None:
        pubsub = self._client.pubsub()
        
        await pubsub.subscribe(channel)
        
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message['data'])
                        await callback(channel, data)
                    except json.JSONDecodeError:
                        await callback(channel, message['data'].decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            raise
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            
    async def close(self) -> None:
        if self._client:
            await self._client.close()
            
