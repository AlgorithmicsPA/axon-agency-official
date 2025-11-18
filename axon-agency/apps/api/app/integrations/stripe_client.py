import stripe
from typing import Optional
from loguru import logger


class StripeClient:
    def __init__(self, secret_key: str, price_id: str, success_url: str, cancel_url: str):
        stripe.api_key = secret_key
        self.price_id = price_id
        self.success_url = success_url
        self.cancel_url = cancel_url
        
        self.key_truncated = secret_key[:15] + "..." if len(secret_key) > 15 else "***"
        logger.info(f"Stripe client initialized. Price ID: {price_id}, Key: {self.key_truncated}")
    
    async def create_checkout(
        self,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[str]:
        """
        Create Stripe checkout session for payment.
        
        Args:
            customer_email: Lead's email (optional but recommended)
            customer_name: Lead's name (optional)
            metadata: Additional metadata to attach to session (optional)
        
        Returns:
            Checkout session URL (str) or None on error
        """
        try:
            session_params = {
                "line_items": [
                    {
                        "price": self.price_id,
                        "quantity": 1
                    }
                ],
                "mode": "payment",
                "success_url": self.success_url,
                "cancel_url": self.cancel_url
            }
            
            if customer_email:
                session_params["customer_email"] = customer_email
            
            if metadata:
                session_params["metadata"] = metadata
            
            checkout_session = stripe.checkout.Session.create(**session_params)
            
            logger.info(
                f"Stripe checkout created. Session ID: {checkout_session.id}, "
                f"Email: {customer_email[:20] if customer_email else 'N/A'}..."
            )
            
            return checkout_session.url
            
        except stripe.error.StripeError as e:
            error_msg = str(e)[:200]
            logger.error(f"Stripe checkout creation failed: {error_msg}")
            return None
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"Stripe error: {error_msg}")
            return None
