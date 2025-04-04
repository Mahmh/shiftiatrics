from argparse import ArgumentParser
from src.server.db import create_shift

if __name__ == '__main__':
    parser = ArgumentParser(description='Create a new shift')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    parser.add_argument('--shift_name', required=True, help='Shift name (e.g., D, E, N)')
    parser.add_argument('--start_time', required=True, help='Start time in HH:MM format (24hr)')
    parser.add_argument('--end_time', required=True, help='End time in HH:MM format (24hr)')
    args = parser.parse_args()

    try:
        shift = create_shift(args.account_id, args.shift_name, args.start_time, args.end_time)
        print(f"✅ Shift created: {shift}")
    except Exception as e:
        print(f"❌ Error creating shift: {e}")