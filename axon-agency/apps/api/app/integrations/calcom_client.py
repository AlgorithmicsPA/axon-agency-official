from typing import Optional
from loguru import logger


class CalComClient:
    def __init__(self, booking_link: str):
        self.booking_link = booking_link
        logger.info(f"Cal.com client initialized. Link: {booking_link}")
    
    def get_booking_link(self, lead_name: Optional[str] = None) -> str:
        """
        Get Cal.com booking link. Can be personalized with query params if needed.
        
        Args:
            lead_name: Optional lead name for personalization
        
        Returns:
            Cal.com booking URL
        """
        if lead_name:
            logger.info(f"Cal.com link generated for: {lead_name[:20]}...")
        
        return self.booking_link
