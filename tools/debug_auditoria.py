import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend import main


if __name__ == '__main__':
    try:
        admin = main.get_user_by_id(1)
        print('admin user:', admin)
        res = main.listar_auditoria(limit=10, user=admin)
        print('result keys:', list(res.keys()))
        import json
        print(json.dumps(res, indent=2, ensure_ascii=False))
    except Exception:
        import traceback
        traceback.print_exc()
