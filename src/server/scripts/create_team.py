from argparse import ArgumentParser
from src.server.db import create_team

if __name__ == '__main__':
    parser = ArgumentParser(description='Create a new team')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    parser.add_argument('--team_name', required=True, help='Team name')
    args = parser.parse_args()

    try:
        team = create_team(args.account_id, args.team_name)
        print(f"✅ Team created: {team}")
    except Exception as e:
        print(f"❌ Error creating team: {e}")