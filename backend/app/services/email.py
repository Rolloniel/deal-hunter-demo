"""Email service using Resend for price alerts."""

import resend
from app.config import get_settings

settings = get_settings()
resend.api_key = settings.resend_api_key


async def send_price_alert(
    to_email: str,
    product_name: str,
    old_price: float,
    new_price: float,
    target_price: float,
    product_url: str = "#",
) -> bool:
    """
    Send a price drop alert email.

    Args:
        to_email: Recipient email address
        product_name: Name of the product
        old_price: Previous price
        new_price: New (lower) price
        target_price: User's target price
        product_url: Link to product (optional)

    Returns:
        True if email sent successfully, False otherwise
    """
    savings = old_price - new_price

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Price Drop Alert</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #18181b; color: #fafafa; padding: 40px 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #27272a; border-radius: 16px; overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); padding: 32px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; color: white;">Price Drop Alert!</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <h2 style="margin: 0 0 16px; font-size: 20px; color: #fafafa;">{product_name}</h2>
                
                <div style="background-color: #3f3f46; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                        <span style="color: #a1a1aa;">Was:</span>
                        <span style="color: #a1a1aa; text-decoration: line-through;">${old_price:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                        <span style="color: #fafafa; font-weight: bold;">Now:</span>
                        <span style="color: #10b981; font-size: 24px; font-weight: bold;">${new_price:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-top: 16px; border-top: 1px solid #52525b;">
                        <span style="color: #10b981;">You save:</span>
                        <span style="color: #10b981; font-weight: bold;">${savings:.2f}</span>
                    </div>
                </div>
                
                <p style="color: #a1a1aa; margin: 0 0 24px; font-size: 14px;">
                    This price is below your target of ${target_price:.2f}. Don't miss out!
                </p>
                
                <a href="{product_url}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); color: white; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    View Deal
                </a>
            </div>
            
            <!-- Footer -->
            <div style="padding: 24px 32px; background-color: #18181b; text-align: center;">
                <p style="margin: 0; color: #71717a; font-size: 12px;">
                    Sent by DealHunter AI
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        params: resend.Emails.SendParams = {
            "from": "DealHunter <alerts@kliuiev.com>",
            "to": [to_email],
            "subject": f"Price Drop: {product_name} now ${new_price:.2f}!",
            "html": html_content,
        }

        email: resend.Emails.SendResponse = resend.Emails.send(params)

        return bool(email.get("id"))

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
