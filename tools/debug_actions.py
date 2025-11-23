import traceback
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
from backend import main

if __name__ == '__main__':
    try:
        # Call with None user (will raise 401 unless DEV_PUBLIC_READ=1), so provide a dummy user dict
        user = {'id': 1, 'username': 'admin', 'rol': 'Administrador'}
        res = main.dashboard_actions_critical(limit=10, user=user)
        print('Result:', res)
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()
