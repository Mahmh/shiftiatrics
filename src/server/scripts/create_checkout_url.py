import argparse, stripe
from src.server.lib.constants import WEB_SERVER_URL

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Stripe Checkout link for a subscription')
    parser.add_argument('--price_id', required=True, help='Stripe Price ID (e.g., price_abc123)')
    args = parser.parse_args()

    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{'price': args.price_id, 'quantity': 1}],
            success_url=f'{WEB_SERVER_URL}/dashboard?chkout_session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{WEB_SERVER_URL}/dashboard'
        )
        print(f'✅ Checkout URL generated:\n{session.url}')
    except Exception as e:
        print(f'❌ Error creating checkout link: {e}')