from abc import ABC, abstractmethod
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class AbstractNotifier(ABC):
    @abstractmethod
    def send_alert(self, title: str, message: str) -> bool:
        pass

class ConsoleNotifier(AbstractNotifier):
    def send_alert(self, title: str, message: str) -> bool:
        print(f"\n{'='*50}\nALERT: {title}\n{message}\n{'='*50}\n")
        logger.info(f"Sent console alert: {title}")
        return True

class DiscordNotifier(AbstractNotifier):
    def __init__(self, webhook_url: Optional[str]):
        self.webhook_url = webhook_url

    def send_alert(self, title: str, message: str) -> bool:
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured. Skipping alert.")
            return False
            
        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 15258703  # A nice color
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully sent Discord alert: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False

class NotifierService:
    def __init__(self, notifiers: list[AbstractNotifier]):
        self.notifiers = notifiers
        
    def dispatch(self, title: str, message: str):
        for notifier in self.notifiers:
            notifier.send_alert(title, message)
