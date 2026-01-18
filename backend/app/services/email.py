async def send_price_alert(
    to_email: str,
    product_name: str,
    old_price: float,
    new_price: float,
    product_url: str = "#",
) -> bool:
    """Send price drop alert email."""
    return True  # Placeholder
