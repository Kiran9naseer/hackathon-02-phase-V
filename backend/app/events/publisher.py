"""Kafka event publisher for system-wide notifications."""

import json
import logging
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
import asyncio

logger = logging.getLogger(__name__)

class KafkaEventPublisher:
    """Publisher for Kafka events."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Initialize the Kafka producer."""
        async with self._lock:
            if self.producer is None:
                try:
                    self.producer = AIOKafkaProducer(
                        bootstrap_servers=self.bootstrap_servers,
                        value_serializer=lambda v: json.dumps(v).encode('utf-8')
                    )
                    await self.producer.start()
                    logger.info(f"Kafka producer started for {self.bootstrap_servers}")
                except Exception as e:
                    logger.error(f"Failed to start Kafka producer: {e}")
                    self.producer = None

    async def stop(self):
        """Stop the Kafka producer."""
        async with self._lock:
            if self.producer:
                await self.producer.stop()
                self.producer = None
                logger.info("Kafka producer stopped")

    async def publish(self, topic: str, data: Dict[str, Any]):
        """Publish an event to a specific topic."""
        if not self.producer:
            await self.start()
            
        if not self.producer:
            logger.warning(f"Kafka producer unavailable. Dropping event on topic {topic}")
            return

        try:
            await self.producer.send_and_wait(topic, data)
            logger.debug(f"Event published to {topic}: {data.get('type')}")
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")

# Global publisher instance
_publisher: Optional[KafkaEventPublisher] = None

async def get_publisher() -> KafkaEventPublisher:
    """Get the global KafkaEventPublisher instance."""
    global _publisher
    if _publisher is None:
        # Connect to localhost by default, can be overridden by ENV if needed
        import os
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        _publisher = KafkaEventPublisher(bootstrap_servers=servers)
        await _publisher.start()
    return _publisher
