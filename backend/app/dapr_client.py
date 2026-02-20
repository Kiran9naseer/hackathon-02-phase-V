"""Dapr client for reminder scheduling and pub/sub.

This module provides a client for interacting with Dapr runtime
for reminder scheduling and event publishing.
"""

import logging
import json
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DaprClient:
    """Client for Dapr runtime interactions.
    
    Provides methods for:
    - Scheduling reminders
    - Publishing events to pub/sub
    - Managing reminder lifecycle
    """
    
    def __init__(self, dapr_host: str = "localhost", dapr_port: int = 3500):
        """Initialize Dapr client.
        
        Args:
            dapr_host: Dapr sidecar host (default: localhost)
            dapr_port: Dapr HTTP port (default: 3500)
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.base_url = f"http://{dapr_host}:{dapr_port}"
        logger.info(f"Dapr client initialized: {self.base_url}")
    
    async def schedule_reminder(
        self,
        name: str,
        due_time: datetime,
        period: str,
        callback: str,
        data: dict
    ) -> bool:
        """Schedule a reminder with Dapr.
        
        Args:
            name: Unique reminder name
            due_time: When to trigger the reminder
            period: How often to repeat (e.g., "PT0S" for once, "P1D" for daily)
            callback: Endpoint to call when triggered
            data: Data to pass to callback
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        import aiohttp
        
        reminder_data = {
            "dueTime": due_time.isoformat(),
            "period": period,
            "callback": callback,
            "data": json.dumps(data)
        }
        
        url = f"{self.base_url}/v1.0/reminders/{name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=reminder_data) as response:
                    if response.status == 204:
                        logger.info(f"Reminder scheduled: {name}")
                        return True
                    else:
                        logger.error(f"Failed to schedule reminder: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}")
            return False
    
    async def cancel_reminder(self, name: str) -> bool:
        """Cancel a scheduled reminder.
        
        Args:
            name: Reminder name to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        import aiohttp
        
        url = f"{self.base_url}/v1.0/reminders/{name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url) as response:
                    if response.status == 204:
                        logger.info(f"Reminder cancelled: {name}")
                        return True
                    else:
                        logger.error(f"Failed to cancel reminder: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error cancelling reminder: {e}")
            return False
    
    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: dict,
        metadata: Optional[dict] = None
    ) -> bool:
        """Publish an event to a topic.
        
        Args:
            pubsub_name: Name of the pub/sub component
            topic: Topic to publish to
            data: Event data to publish
            metadata: Optional metadata
            
        Returns:
            True if published successfully, False otherwise
        """
        import aiohttp
        
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=metadata or {}) as response:
                    if response.status == 204:
                        logger.info(f"Event published to {topic}")
                        return True
                    else:
                        logger.error(f"Failed to publish event: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False


# Global Dapr client instance
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get or create the global Dapr client instance.
    
    Returns:
        DaprClient instance
    """
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
