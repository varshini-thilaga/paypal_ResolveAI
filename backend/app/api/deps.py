from typing import Optional
from fastapi import Depends
from backend.app.core.config import Settings, get_settings
from backend.app.core.security import PaymentAuthorizationManager
from backend.app.services.paypal_client import PayPalClient

_auth_manager_instance: Optional[PaymentAuthorizationManager] = None
_paypal_client_instance: Optional[PayPalClient] = None


def get_auth_manager(settings: Settings = Depends(get_settings)) -> PaymentAuthorizationManager:
    """Returns singleton instance of PaymentAuthorizationManager."""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = PaymentAuthorizationManager(
            secret_key=settings.SESSION_SECRET.get_secret_value()
        )
    return _auth_manager_instance


def get_paypal_client(
    settings: Settings = Depends(get_settings),
    auth_manager: PaymentAuthorizationManager = Depends(get_auth_manager)
) -> PayPalClient:
    """Returns singleton instance of PayPalClient."""
    global _paypal_client_instance
    if _paypal_client_instance is None:
        _paypal_client_instance = PayPalClient(settings=settings, auth_manager=auth_manager)
    return _paypal_client_instance
