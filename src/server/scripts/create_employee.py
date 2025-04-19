from argparse import ArgumentParser
from src.server.db import create_employee

if __name__ == '__main__':
    parser = ArgumentParser(description='Create a new employee')
    parser.add_argument('--account_id', type=int, required=True, help='Account ID')
    parser.add_argument('--employee_name', required=True, help='Employee name')
    parser.add_argument('--min_work_hours', type=int, help='Minimum work hours per month')
    parser.add_argument('--max_work_hours', type=int, help='Maximum work hours per month')
    args = parser.parse_args()

    try:
        employee = create_employee(args.account_id, args.employee_name, args.min_work_hours, args.max_work_hours)
        print(f"✅ Employee created: {employee}")
    except Exception as e:
        print(f"❌ Error creating employee: {e}")