"""Kafka event consumer for real-time broadcasting."""

import json
import logging
import asyncio
from aiokafka import AIOKafkaConsumer
from app.api.events import notify_user

logger = logging.getLogger(__name__)

class KafkaEventConsumer:
    """Consumer for Kafka events to broadcast via SSE/WS."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092", topics: list[str] = ["task_events", "notification_events"]):
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.consumer = None
        self._running = False

    async def start(self):
        """Start the Kafka consumer loop."""
        self._running = True
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id="notification-group",
                auto_offset_reset="latest",
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            await self.consumer.start()
            logger.info(f"Kafka consumer started for topics {self.topics}")
            
            async for msg in self.consumer:
                if not self._running:
                    break
                
                event_data = msg.value
                user_id = event_data.get("user_id")
                event_type = event_data.get("type")
                
                if user_id and event_type:
                    # Broadcast to SSE via EventManager
                    await notify_user(user_id, event_type, event_data)
                    logger.debug(f"Broadcasted {event_type} to user {user_id}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")
        finally:
            if self.consumer:
                await self.consumer.stop()
            self._running = False
            logger.info("Kafka consumer stopped")

    def stop(self):
        """Signal the consumer to stop."""
        self._running = False

# Global consumer instance reference
_consumer_task = None

async def start_event_consumer():
    """Start the global event consumer background task."""
    import os
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    consumer = KafkaEventConsumer(bootstrap_servers=servers)
    return asyncio.create_task(consumer.start())
