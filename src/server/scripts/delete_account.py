from argparse import ArgumentParser
from src.server.db import delete_account

if __name__ == '__main__':
    parser = ArgumentParser(description='Delete an existing account')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    args = parser.parse_args()

    try:
        delete_account(args.account_id)
        print(f"✅ Account deleted: {args.account_id}")
    except Exception as e:
        print(f"❌ Error deleting account: {e}")