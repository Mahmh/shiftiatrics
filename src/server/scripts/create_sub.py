from argparse import ArgumentParser
from datetime import datetime
from src.server.lib.constants import PLAN_NAMES
from src.server.db import create_sub

if __name__ == '__main__':
    parser = ArgumentParser(description='Create a subscription for an account')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    parser.add_argument('--plan', required=True, choices=PLAN_NAMES, help='Subscription plan name')
    parser.add_argument('--expires_at', required=True, help='Expiration date in YYYY-MM-DD format')
    parser.add_argument('--stripe_subscription_id', required=True, help='Stripe subscription ID')
    parser.add_argument('--stripe_customer_id', required=True, help='Stripe customer ID')
    args = parser.parse_args()

    try:
        account, sub = create_sub(
            account_id=args.account_id,
            plan=args.plan,
            expires_at=datetime.strptime(args.expires_at, '%Y-%m-%d'),
            stripe_subscription_id=args.stripe_subscription_id,
            stripe_customer_id=args.stripe_customer_id
        )
        print(f"✅ Subscription created: {sub} for account {account.email}")
    except Exception as e:
        print(f"❌ Error creating subscription: {e}")