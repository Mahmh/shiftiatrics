from argparse import ArgumentParser
from datetime import timedelta
import json
import stripe
from src.server.db import save_custom_plan_metadata
from src.server.lib.models import PlanDetails
from src.server.lib.utils import utcnow
from src.server.lib.constants import WEB_SERVER_URL

if __name__ == '__main__':
    parser = ArgumentParser(description='Prepare a custom plan checkout session for a specific account.')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    parser.add_argument('--price', type=float, required=True, help='Price of the custom plan (e.g. 129.99)')
    parser.add_argument('--days', type=int, default=30, help='How many days the plan lasts (default: 30)')
    parser.add_argument('--plan_details', type=str, required=True, help='JSON string of plan details')
    args = parser.parse_args()

    # Parse plan_details safely
    try:
        plan_details_data = json.loads(args.plan_details.strip())
        plan_details = PlanDetails(**plan_details_data)
    except Exception as e:
        raise ValueError(f'Invalid plan_details JSON: {e}')

    print('⚙️  Creating Stripe product, price, and checkout session...')

    # Create product
    product = stripe.Product.create(
        name=f'Custom Plan for Account {args.account_id}',
        description='Custom subscription plan created via CLI.',
        metadata={'account_id': str(args.account_id)}
    )

    # Create price
    price_obj = stripe.Price.create(
        unit_amount=int(args.price * 100),
        currency='usd',
        recurring={'interval': 'month'},
        product=product.id,
        lookup_key=f'custom_{args.account_id}'
    )

    # Create checkout session
    session_obj = stripe.checkout.Session.create(
        mode='subscription',
        line_items=[{
            'price': price_obj.id,
            'quantity': 1,
        }],
        success_url=f'{WEB_SERVER_URL}/dashboard?chkout_session_id={{CHECKOUT_SESSION_ID}}&plan=custom',
        cancel_url=f'{WEB_SERVER_URL}/dashboard',
    )

    # Store pending session ID and plan metadata
    save_custom_plan_metadata(
        account_id=args.account_id,
        stripe_product_id=product.id,
        stripe_price_id=price_obj.id,
        stripe_checkout_url=session_obj.url,
        plan_details=plan_details,
        price=args.price,
        expires_at=utcnow() + timedelta(days=args.days)
    )

    print(f'\n✅ Created pending checkout for account {args.account_id}')
    print(f'   ↳ Price: ${args.price}')
    print(f'   ↳ Stripe Product ID: {product.id}')
    print(f'   ↳ Stripe Price ID: {price_obj.id}')
    print(f'   ↳ Stripe Lookup Key: custom_{args.account_id}')
    print(f'   ↳ Checkout URL: {session_obj.url}')
    print(f'   ↳ Session ID stored in DB: {session_obj.id}')