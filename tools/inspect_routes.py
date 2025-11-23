import sys
import importlib
sys.path.insert(0, r'D:\DEVFULLAPP\appPHAV3')
try:
    m = importlib.import_module('backend.main')
    paths = [r.path for r in m.app.routes]
    print('ROUTES_COUNT', len(paths))
    for p in paths:
        print(p)
except Exception as e:
    import traceback
    traceback.print_exc()
